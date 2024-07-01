import os
import json
import geojson
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from loguru import logger as log

from app.projects import project_schemas, project_crud
from app.db import database
from app.models.enums import HTTPStatus
from app.utils import multipolygon_to_polygon
from app.s3 import s3_client
from app.config import settings
from databases import Database
from app.db import db_models

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/projects",
    responses={404: {"description": "Not found"}},
)


@router.delete("/{project_id}", tags=["Projects"])
def delete_project_by_id(project_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a project by its ID, along with all associated tasks.

    Args:
        project_id (int): The ID of the project to delete.
        db (Session): The database session dependency.

    Returns:
        dict: A confirmation message.

    Raises:
        HTTPException: If the project is not found.
    """
    # Query for the project
    project = (
        db.query(db_models.DbProject)
        .filter(db_models.DbProject.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Query and delete associated tasks
    tasks = (
        db.query(db_models.DbTask)
        .filter(db_models.DbTask.project_id == project_id)
        .all()
    )
    for task in tasks:
        db.delete(task)

    # Delete the project
    db.delete(project)
    db.commit()
    return {"message": f"Project ID: {project_id} is deleted successfully."}


@router.post(
    "/create_project", tags=["Projects"], response_model=project_schemas.ProjectOut
)
async def create_project(
    project_info: project_schemas.ProjectIn,
    db: Database = Depends(database.encode_db),
):
    """Create a project in  database."""
    project = await project_crud.create_project_with_project_info(db, project_info)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Project creation failed"
        )
    return project


@router.post("/{project_id}/upload-task-boundaries", tags=["Projects"])
async def upload_project_task_boundaries(
    project_id: int,
    task_geojson: UploadFile = File(...),
    db: Database = Depends(database.encode_db),
):
    """Set project task boundaries using split GeoJSON from frontend.

    Each polygon in the uploaded geojson are made into single task.

    Required Parameters:
        project_id (id): ID for associated project.
        task_geojson (UploadFile): Multi-polygon GeoJSON file.

    Returns:
        dict: JSON containing success message, project ID, and number of tasks.
    """    
    #check the project in Database
    raw_sql = f"""SELECT id FROM projects WHERE id = '{project_id}' LIMIT 1;"""
    project =  await db.fetch_one(query=raw_sql)
    if not project:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Project not found.")

    # read entire file
    content = await task_geojson.read()
    task_boundaries = json.loads(content)
    task_boundaries = multipolygon_to_polygon(task_boundaries)

    log.debug("Creating tasks for each polygon in project")
    await project_crud.create_tasks_from_geojson(db, project_id, task_boundaries)

    return {"message": "Project Boundary Uploaded", "project_id": f"{project_id}"}


@router.post("/preview-split-by-square/", tags=["Projects"])
async def preview_split_by_square(
    project_geojson: UploadFile = File(...), dimension: int = Form(100)
):
    """Preview splitting by square."""

    # Validating for .geojson File.
    file_name = os.path.splitext(project_geojson.filename)
    file_ext = file_name[1]
    allowed_extensions = [".geojson", ".json"]
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Provide a valid .geojson file")

    # read entire file
    content = await project_geojson.read()
    boundary = geojson.loads(content)

    result = await project_crud.preview_split_by_square(boundary, dimension)
    return result


@router.post("/generate-presigned-url/", tags=["Image Upload"])
async def generate_presigned_url(data: project_schemas.PresignedUrlRequest):
    """
    Generate a pre-signed URL for uploading an image to S3 Bucket.

    This endpoint generates a pre-signed URL that allows users to upload an image to
    an S3 bucket. The URL expires after a specified duration.

    Args:

        image_name: The name of the image you want to upload
        expiry : Expiry time in hours

    Returns:

        str: The pre-signed URL to upload the image
    """
    try:
        # Generate a pre-signed URL for an object
        client = s3_client()

        url = client.presigned_put_object(
            settings.S3_BUCKET_NAME,
            f"publicuploads/{data.image_name}",
            expires=timedelta(hours=data.expiry),
        )

        return url
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Failed to generate pre-signed URL. {e}",
        )


@router.get("/", tags=["Projects"], response_model=list[project_schemas.ProjectOut])
async def read_projects(
    skip: int = 0, limit: int = 100, db: Database = Depends(database.encode_db)
):
    "Return all projects"
    projects = await project_crud.get_projects(db, skip, limit)
    return projects


@router.get(
    "/{project_id}", tags=["Projects"])
async def read_project(
    project_id: int,
    db: Session = Depends(database.encode_db),
):
    """Get a specific project and all associated tasks by ID."""
    project = await project_crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project