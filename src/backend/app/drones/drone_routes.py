from typing import Annotated
from app.users.user_deps import login_required
from app.users.user_schemas import AuthUser
from app.models.enums import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from app.db import database
from app.config import settings
from app.drones import drone_schemas
from psycopg import Connection
from app.drones import drone_crud
from typing import List


router = APIRouter(
    prefix=f"{settings.API_PREFIX}/drones",
    responses={404: {"description": "Not found"}},
)


@router.get("/", tags=["Drones"], response_model=List[drone_schemas.DroneOut])
async def read_drones(
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """
    Retrieves all drone records from the database.

    Args:
        db (Database, optional): The database session object.
        user_data (AuthUser, optional): The authenticated user data.

    Returns:
        List[drone_schemas.DroneOut]: A list of all drone records.
    """
    drones = await drone_crud.read_all_drones(db)
    return drones


@router.delete("/{drone_id}", tags=["Drones"])
async def delete_drone(
    drone_id: int,
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """
    Deletes a drone record from the database.

    Args:
        drone_id (int): The ID of the drone to be deleted.
        db (Database, optional): The database session object.
        user_data (AuthUser, optional): The authenticated user data.

    Returns:
        dict: A success message if the drone was deleted.
    """
    success = await drone_crud.delete_drone(db, drone_id)
    if not success:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Drone not found")
    return {"message": "Drone deleted successfully"}


@router.post("/create_drone", tags=["Drones"])
async def create_drone(
    drone_info: drone_schemas.DroneIn,
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """
    Creates a new drone record in the database.

    Args:
        drone_info (drone_schemas.DroneIn): The schema object containing drone details.
        db (Database, optional): The database session object.
        user_data (AuthUser, optional): The authenticated user data.

    Returns:
        dict: A dictionary containing a success message and the ID of the newly created drone.
    """
    drone_id = await drone_crud.create_drone(db, drone_info)
    if not drone_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Drone creation failed"
        )
    return {"message": "Drone created successfully", "drone_id": drone_id}


@router.get("/{drone_id}", tags=["Drones"], response_model=drone_schemas.DroneOut)
async def read_drone(
    drone_id: int,
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """
    Retrieves a drone record from the database.

    Args:
        drone_id (int): The ID of the drone to be retrieved.
        db (Database, optional): The database session object.
        user_data (AuthUser, optional): The authenticated user data.

    Returns:
        dict: The drone record if found.
    """
    drone = await drone_crud.get_drone(db, drone_id)
    if not drone:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Drone not found")
    return drone
