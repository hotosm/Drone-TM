import time
import jwt
from app.config import settings
from typing import Any
from passlib.context import CryptContext
from app.db import db_models
from app.users.user_schemas import AuthUser, ProfileUpdate
from fastapi import HTTPException
from pydantic import EmailStr
from psycopg import Connection


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_access_token(subject: str | Any):
    expire = int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_expire = int(time.time()) + settings.REFRESH_TOKEN_EXPIRE_MINUTES

    # access token
    subject["exp"] = expire
    access_token = jwt.encode(
        subject, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    # refresh token
    subject["exp"] = refresh_expire
    refresh_token = jwt.encode(
        subject, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return access_token, refresh_token


def verify_token(token: str):
    """Verifies the access token and returns the payload if valid.

    Args:
        token (str): The access token to be verified.

    Returns:
        dict: The payload of the access token if verification is successful.

    Raises:
        HTTPException: If the token has expired or credentials could not be validated.
    """
    secret_key = settings.SECRET_KEY
    try:
        return jwt.decode(token, str(secret_key), algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate token") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_by_id(db: Connection, id: str):
    query = "SELECT * FROM users WHERE id = :id LIMIT 1;"
    result = await db.fetch_one(query, {"id": id})
    return result


async def get_userprofile_by_userid(db: Connection, user_id: str):
    query = "SELECT * FROM user_profile WHERE user_id = :user_id LIMIT 1;"
    result = await db.fetch_one(query, {"user_id": user_id})
    return result


async def get_user_by_email(db: Connection, email: str):
    query = "SELECT * FROM users WHERE email_address = :email LIMIT 1;"
    result = await db.fetch_one(query, {"email": email})
    return result


async def authenticate(
    db: Connection, email: EmailStr, password: str
) -> db_models.DbUser | None:
    db_user = await get_user_by_email(db, email)
    if not db_user:
        return None
    if not verify_password(password, db_user["password"]):
        return None
    return db_user


async def get_or_create_user(
    db: Connection,
    user_data: AuthUser,
):
    """Get user from User table if exists, else create."""
    try:
        update_sql = """
            INSERT INTO users (
                    id, name, email_address, profile_img, is_active, is_superuser, date_registered
                    )
                VALUES (
                    :user_id, :name, :email_address, :profile_img, True, False, now()
                    )
            ON CONFLICT (id)
                DO UPDATE SET profile_img = :profile_img;
            """

        await db.execute(
            update_sql,
            {
                "user_id": str(user_data.id),
                "name": user_data.name,
                "email_address": user_data.email,
                "profile_img": user_data.img_url,
            },
        )
        return user_data

    except Exception as e:
        if (
            'duplicate key value violates unique constraint "users_email_address_key"'
            in str(e)
        ):
            raise HTTPException(
                status_code=400,
                detail=f"User with this email {user_data.email} already exists.",
            ) from e
        else:
            raise HTTPException(status_code=400, detail=str(e)) from e


async def update_user_profile(
    db: Connection, user_id: int, profile_update: ProfileUpdate
):
    """
    Update user profile in the database.
    Args:
        db (Database): Database connection object.
        user_id (int): ID of the user whose profile is being updated.
        profile_update (ProfileUpdate): Instance of ProfileUpdate containing fields to update.
    Returns:
        bool: True if update operation succeeds.
    Raises:
        Any exceptions thrown during database operations.
    """

    try:
        profile_query = """
        INSERT INTO user_profile (user_id, role, phone_number, country, city, organization_name, organization_address, job_title, notify_for_projects_within_km,
                                    experience_years, drone_you_own, certified_drone_operator)
        VALUES (:user_id, :role, :phone_number, :country, :city, :organization_name, :organization_address, :job_title, :notify_for_projects_within_km ,
                :experience_years, :drone_you_own, :certified_drone_operator)
        ON CONFLICT (user_id)
        DO UPDATE SET
            role = :role,
            phone_number = :phone_number,
            country = :country,
            city = :city,
            organization_name = :organization_name,
            organization_address = :organization_address,
            job_title = :job_title,
            notify_for_projects_within_km = :notify_for_projects_within_km,
            experience_years = :experience_years,
            drone_you_own = :drone_you_own,
            certified_drone_operator = :certified_drone_operator;
        """

        await db.execute(
            profile_query,
            {
                "user_id": user_id,
                "role": profile_update.role,
                "phone_number": profile_update.phone_number,
                "country": profile_update.country,
                "city": profile_update.city,
                "organization_name": profile_update.organization_name,
                "organization_address": profile_update.organization_address,
                "job_title": profile_update.job_title,
                "notify_for_projects_within_km": profile_update.notify_for_projects_within_km,
                "experience_years": profile_update.experience_years,
                "drone_you_own": profile_update.drone_you_own,
                "certified_drone_operator": profile_update.certified_drone_operator,
            },
        )

        # If password is provided, update the users table
        if profile_update.password:
            password_update_query = """
            UPDATE users
            SET password = :password
            WHERE id = :user_id;
            """
            await db.execute(
                password_update_query,
                {
                    "password": get_password_hash(profile_update.password),
                    "user_id": user_id,
                },
            )

        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
