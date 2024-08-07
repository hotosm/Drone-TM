import os
from fastapi import APIRouter, Response, HTTPException, Depends, Request
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.users.user_schemas import (
    Token,
    ProfileUpdate,
    AuthUser,
)
from app.users.user_deps import login_required, init_google_auth
from app.config import settings
from app.users import user_crud
from app.db import database
from app.models.enums import HTTPStatus
from psycopg import Connection
from fastapi.responses import JSONResponse
from loguru import logger as log


if settings.DEBUG:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


router = APIRouter(
    prefix=f"{settings.API_PREFIX}/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login/")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Connection, Depends(database.get_db)],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_crud.authenticate(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    user_info = {
        "id": user.id,
        "email": user.email_address,
        "name": user.name,
        "img_url": user.profile_img,
    }

    access_token, refresh_token = await user_crud.create_access_token(user_info)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.patch("/{user_id}/profile")
@router.post("/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    profile_update: ProfileUpdate,
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """
    Update user profile based on provided user_id and profile_update data.
    Args:
        user_id (int): The ID of the user whose profile is being updated.
        profile_update (UserProfileUpdate): Updated profile data to apply.
    Returns:
        dict: Updated user profile information.
    Raises:
        HTTPException: If user with given user_id is not found in the database.
    """

    user = await user_crud.get_user_by_id(db, user_id)
    if user_data.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not authorized to update profile",
        )

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    user = await user_crud.update_user_profile(db, user_id, profile_update)
    return Response(status_code=HTTPStatus.OK)


@router.get("/google-login")
async def login_url(google_auth=Depends(init_google_auth)):
    """Get Login URL for Google Oauth Application.

    The application must be registered on google oauth.
    Open the download url returned to get access_token.

    Args:
        request: The GET request.
        google_auth: The Auth object.

    Returns:
        login_url (string): URL to authorize user in Google OAuth.
            Includes URL params: client_id, redirect_uri, permission scope.
    """
    login_url = google_auth.login()
    log.debug(f"Login URL returned: {login_url}")
    return JSONResponse(content=login_url, status_code=200)


@router.get("/callback/")
async def callback(request: Request, google_auth=Depends(init_google_auth)):
    """Performs token exchange between Google and DTM API"""

    # Enforce https callback url
    callback_url = str(request.url).replace("http://", "https://")

    access_token = google_auth.callback(callback_url).get("access_token")

    user_data = google_auth.deserialize_access_token(access_token)
    access_token, refresh_token = await user_crud.create_access_token(user_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/refresh-token", response_model=Token)
async def update_token(user_data: Annotated[AuthUser, Depends(login_required)]):
    """Refresh access token"""

    access_token, refresh_token = await user_crud.create_access_token(
        user_data.model_dump()
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/my-info/")
async def my_data(
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """Read access token and get user details from Google"""

    user_info = await user_crud.get_or_create_user(db, user_data)
    has_user_profile = await user_crud.get_userprofile_by_userid(db, user_info.id)

    user_info_dict = user_info.model_dump()
    user_info_dict["has_user_profile"] = bool(has_user_profile)
    return user_info_dict
