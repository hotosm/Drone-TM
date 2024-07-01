import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.projects import project_schemas
from app.db import db_models
from loguru import logger as log
import shapely.wkb as wkblib
from shapely.geometry import shape
from fastapi import HTTPException
from app.utils import merge_multipolygon, str_to_geojson
from fmtm_splitter.splitter import split_by_square
from fastapi.concurrency import run_in_threadpool
from app.db import database
from fastapi import Depends
from asyncio import gather
from databases import Database
from app.models.enums import HTTPStatus


async def create_project_with_project_info(
    db: Database, project_metadata: project_schemas.ProjectIn
):
    """Create a project in database."""
    query = f"""
    INSERT INTO projects (
        author_id, name, short_description, description, per_task_instructions, status, visibility, mapper_level, priority, outline, created
    )
    VALUES (
        1,
        '{project_metadata.name}',
        '{project_metadata.short_description}',
        '{project_metadata.description}',
        '{project_metadata.per_task_instructions}',
        'DRAFT',
        'PUBLIC',
        'INTERMEDIATE',
        'MEDIUM',
        '{str(project_metadata.outline)}',
        CURRENT_TIMESTAMP
    )
    RETURNING id
    """
    new_project_id = await db.execute(query)

    if not new_project_id:
        raise HTTPException(status_code=500, detail="Project could not be created")
    # Fetch the newly created project using the returned ID
    select_query = f"""
        SELECT id, name, short_description, description, per_task_instructions, outline
        FROM projects
        WHERE id = '{new_project_id}'
    """
    new_project = await db.fetch_one(query=select_query)
    return new_project


async def get_project_by_id(
    db: Database = Depends(database.encode_db), project_id: Optional[int] = None
) -> db_models.DbProject:
    """Get a single project &  all associated tasks by ID."""
    #check the project in Database
    raw_sql = f"""SELECT id, short_description,total_tasks FROM projects WHERE id = '{project_id}' LIMIT 1;"""
    raw_sql = f"""
    SELECT 
        projects.id, 
        projects.short_description, 
        projects.description,
        projects.author_id,
        users.name AS author_name
    FROM projects 
    JOIN users ON projects.author_id = users.id 
    WHERE projects.id = '{project_id}' 
    LIMIT 1;
    """

    project =  await db.fetch_one(query=raw_sql)
    if not project:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Project not found.")

    # get tasks of project
    query = f""" SELECT * from tasks WHERE project_id = '{project_id}';"""
    all_tasks = await db.fetch_all(query=query)    
    tasks =   await convert_to_app_tasks(all_tasks)
    # Count the total tasks
    task_count = len(tasks)
    return {
        "project": project,
        "task_count": task_count,
        "tasks": tasks,
    }
    
async def convert_to_app_tasks(
    db_tasks: List[db_models.DbTask],
) -> List[project_schemas.TaskOut]:
    """Legacy function to convert db models --> Pydantic.

    TODO refactor to use Pydantic model methods instead.
    """
    if db_tasks and len(db_tasks) > 0:

        async def convert_task(task):
            return await convert_to_app_task(task)

        app_tasks = await gather(
            *[convert_task(task) for task in db_tasks]
        )        
        return [task for task in app_tasks if task is not None]
    else:
        return []    


async def get_projects(
    db: Database,
    skip: int = 0,
    limit: int = 100,
):
    """Get all projects."""
    raw_sql = """
        SELECT id, name, short_description, description, per_task_instructions, outline
        FROM projects
        ORDER BY id DESC
        OFFSET :skip
        LIMIT :limit;
        """
    db_projects = await db.fetch_all(raw_sql, {"skip": skip, "limit": limit})
    return await convert_to_app_projects(db_projects)


async def convert_to_app_projects(
    db_projects: List[db_models.DbProject],
) -> List[project_schemas.ProjectOut]:
    """Legacy function to convert db models --> Pydantic.

    TODO refactor to use Pydantic model methods instead.
    """
    if db_projects and len(db_projects) > 0:

        async def convert_project(project):
            return await convert_to_app_project(project)

        app_projects = await gather(
            *[convert_project(project) for project in db_projects]
        )
        return [project for project in app_projects if project is not None]
    else:
        return []


async def convert_to_app_project(db_project: db_models.DbProject):
    """Legacy function to convert db models --> Pydantic."""
    if not db_project:
        log.debug("convert_to_app_project called, but no project provided")
        return None
    app_project = db_project

    if db_project.outline:
        app_project.outline_geojson = str_to_geojson(
            db_project.outline, {"id": db_project.id}, db_project.id
        )
    return app_project

async def convert_to_app_task(db_task: db_models.DbTask):
    """Legacy function to convert db models --> Pydantic."""
    if not db_task:
        return None
    app_task = db_task

    if app_task.outline:
        
        app_task = str_to_geojson(
            app_task.outline, {"id": app_task.id}, app_task.id
        )
    return app_task


async def create_tasks_from_geojson(
    db: Database,
    project_id: int,
    boundaries: str,
):
    """Create tasks for a project, from provided task boundaries."""
    try:
        if isinstance(boundaries, str):
            boundaries = json.loads(boundaries)

        # Update the boundary polyon on the database.
        if boundaries["type"] == "Feature":
            polygons = [boundaries]
        else:
            polygons = boundaries["features"]
        log.debug(f"Processing {len(polygons)} task geometries")
        for index, polygon in enumerate(polygons):
            # If the polygon is a MultiPolygon, convert it to a Polygon
            if polygon["geometry"]["type"] == "MultiPolygon":
                log.debug("Converting MultiPolygon to Polygon")
                polygon["geometry"]["type"] = "Polygon"
                polygon["geometry"]["coordinates"] = polygon["geometry"]["coordinates"][
                    0
                ]
            query = f""" INSERT INTO tasks (project_id,outline,project_task_index) VALUES ( '{project_id}', '{wkblib.dumps(shape(polygon["geometry"]), hex=True)}', '{index + 1}');"""

            result = await db.execute(query)
            if result:
                log.debug(
                    "Created database task | "
                    f"Project ID {project_id} | "
                    f"Task index {index}"
                )
                log.debug(
                    "COMPLETE: creating project boundary, based on task boundaries"
                )
                return True
    except Exception as e:
        log.exception(e)
        raise HTTPException(e) from e


async def preview_split_by_square(boundary: str, meters: int):
    """Preview split by square for a project boundary.

    Use a lambda function to remove the "z" dimension from each
    coordinate in the feature's geometry.
    """
    boundary = merge_multipolygon(boundary)

    return await run_in_threadpool(
        lambda: split_by_square(
            boundary,
            meters=meters,
        )
    )
