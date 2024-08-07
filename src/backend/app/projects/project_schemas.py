import json
import uuid
from typing import Annotated, Optional, List
from datetime import datetime, date

import geojson
from loguru import logger as log
from pydantic import BaseModel, computed_field, Field
from pydantic.functional_validators import AfterValidator
from pydantic.functional_serializers import PlainSerializer
from geojson_pydantic import Feature, FeatureCollection, Polygon, Point, MultiPolygon
from fastapi import HTTPException
from psycopg import Connection
from psycopg.rows import class_row
from slugify import slugify

from app.models.enums import FinalOutput, ProjectVisibility, State
from app.models.enums import (
    IntEnum,
    ProjectStatus,
    HTTPStatus,
)
from app.utils import (
    merge_multipolygon,
)


def validate_geojson(
    value: FeatureCollection | Feature | Polygon,
) -> geojson.FeatureCollection:
    """Convert the upload GeoJSON to standardised FeatureCollection."""
    return merge_multipolygon(value.model_dump())


def enum_to_str(value: IntEnum) -> str:
    """Get the string value of the enum for db insert."""
    return value.name


class ProjectIn(BaseModel):
    """Upload new project."""

    name: str
    description: str
    per_task_instructions: Optional[str] = None
    task_split_dimension: Optional[int] = None
    dem_url: Optional[str] = None
    gsd_cm_px: float = None
    is_terrain_follow: bool = False
    outline: Annotated[
        FeatureCollection | Feature | Polygon, AfterValidator(validate_geojson)
    ]
    no_fly_zones: Annotated[
        Optional[FeatureCollection | Feature | Polygon],
        AfterValidator(validate_geojson),
    ] = None
    output_orthophoto_url: Optional[str] = None
    output_pointcloud_url: Optional[str] = None
    output_raw_url: Optional[str] = None
    deadline_at: Optional[date] = None
    visibility: Annotated[ProjectVisibility | str, PlainSerializer(enum_to_str)] = (
        ProjectVisibility.PUBLIC
    )
    status: Annotated[ProjectStatus | str, PlainSerializer(enum_to_str)] = (
        ProjectStatus.PUBLISHED
    )
    final_output: List[FinalOutput] = Field(
        ...,
        example=[
            "ORTHOPHOTO_2D",
            "ORTHOPHOTO_3D",
            "DIGITAL_TERRAIN_MODEL",
            "DIGITAL_SURFACE_MODEL",
        ],
    )
    requires_approval_from_manager_for_locking: Optional[bool] = False
    front_overlap: Optional[float] = None
    side_overlap: Optional[float] = None

    @computed_field
    @property
    def slug(self) -> str:
        """
        Generate a unique slug based on the provided name.

        The slug is created by converting the given name into a URL-friendly format and appending
        the current date and time to ensure uniqueness. The date and time are formatted as
        "ddmmyyyyHHMM" to create a timestamp.

        Args:
            name (str): The name from which the slug will be generated.

        Returns:
            str: The generated slug, which includes the URL-friendly version of the name and
                a timestamp. If an error occurs during the generation, an empty string is returned.

        Raises:
            Exception: If an error occurs during the slug generation process.
        """
        try:
            slug = slugify(self.name)
            now = datetime.now()
            date_time_str = now.strftime("%d%m%Y%H%M")
            slug_with_date = f"{slug}-{date_time_str}"
            return slug_with_date
        except Exception as e:
            log.error(f"An error occurred while generating the slug: {e}")
            return ""


class TaskOut(BaseModel):
    """Base project model."""

    id: uuid.UUID
    project_task_index: int
    outline: Polygon
    state: Optional[State] = None
    contributor: Optional[str] = None


class DbProject(BaseModel):
    """Project model for extracting from database."""

    id: uuid.UUID
    name: str
    slug: Optional[str] = None
    short_description: Optional[str]
    description: str
    per_task_instructions: Optional[str] = None
    organisation_id: Optional[int]
    outline: Polygon
    centroid: Optional[Point]
    no_fly_zones: Optional[MultiPolygon]
    task_count: int = 0
    tasks: Optional[list[TaskOut]] = []
    # TODO add all remaining project fields and validators

    @staticmethod
    async def one(db: Connection, project_id: uuid.UUID):
        """Get a single project by it's ID, including tasks and task count."""
        async with db.cursor(row_factory=class_row(DbProject)) as cur:
            # NOTE to wrap Polygon geometry in Feature
            # jsonb_build_object(
            #     'type', 'Feature',
            #     'geometry', ST_AsGeoJSON(p.outline)::jsonb,
            #     'id', p.id::varchar,
            #     'properties', jsonb_build_object()
            # ) AS outline,
            await cur.execute(
                """
                SELECT
                    p.*,
                    ST_AsGeoJSON(p.outline)::jsonb AS outline,
                    ST_AsGeoJSON(p.centroid)::jsonb AS centroid,
                    COALESCE(JSON_AGG(t.*) FILTER (WHERE t.id IS NOT NULL), '[]'::json) AS tasks,
                    COUNT(t.id) AS task_count
                FROM
                    projects p
                LEFT JOIN
                    tasks t ON p.id = t.project_id
                WHERE
                    p.id = %(project_id)s
                GROUP BY
                    p.id;
                """,
                {"project_id": project_id},
            )
            project = await cur.fetchone()

            if not project:
                raise KeyError(f"Project {project_id} not found")

            return project

    @staticmethod
    async def all(db: Connection, skip: int = 0, limit: int = 100):
        """Get all projects, including tasks and task count."""
        async with db.cursor(row_factory=class_row(DbProject)) as cur:
            await cur.execute(
                """
                SELECT
                    p.*,
                    ST_AsGeoJSON(p.outline)::jsonb AS outline,
                    ST_AsGeoJSON(p.centroid)::jsonb AS centroid,
                    COALESCE(JSON_AGG(t.*) FILTER (WHERE t.id IS NOT NULL), '[]'::json) AS tasks,
                    COUNT(t.id) AS task_count
                FROM
                    projects p
                LEFT JOIN
                    tasks t ON p.id = t.project_id
                GROUP BY
                    p.id
                ORDER BY
                    created_at DESC
                OFFSET %(skip)s
                LIMIT %(limit)s;
                """,
                {"skip": skip, "limit": limit},
            )
            projects = await cur.fetchall()

            if not projects:
                raise KeyError("No projects found")

            return projects

    @staticmethod
    async def create(db: Connection, project: ProjectIn, user_id: str) -> uuid.UUID:
        """Create a single project."""
        # NOTE we first check if a project with this name exists
        # It is easier to do this than complex upsert logic
        async with db.cursor() as cur:
            sql = """
                SELECT EXISTS (
                    SELECT 1
                    FROM projects
                    WHERE LOWER(name) = %(name)s
                )
            """
            await cur.execute(sql, {"name": project.name.lower()})
            project_exists = await cur.fetchone()
            if project_exists[0]:
                msg = f"Project name ({project.name}) already exists!"
                log.warning(f"User ({user_id}) failed project creation: {msg}")
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=msg)

        # NOTE exclude_none is used over exclude_unset, or default value are not included
        model_dump = project.model_dump(
            exclude_none=True, exclude=["outline", "centroid"]
        )
        columns = ", ".join(model_dump.keys())
        value_placeholders = ", ".join(f"%({key})s" for key in model_dump.keys())
        sql = f"""
            INSERT INTO projects (
                id, author_id, outline, centroid, created_at, {columns}
            )
            VALUES (
                gen_random_uuid(),
                %(author_id)s,
                ST_GeomFromGeoJSON(%(outline)s),
                ST_Centroid(ST_GeomFromGeoJSON(%(outline)s)),
                NOW(),
                {value_placeholders}
            )
            RETURNING id;
        """
        # We only want the first geometry (they should be merged previously)
        outline_geometry = json.dumps(project.outline["features"][0]["geometry"])
        # Add required author_id and outline as json
        model_dump.update(
            {
                "author_id": user_id,
                "outline": outline_geometry,
            }
        )
        # Append no fly zones if they are present
        # FIXME they are merged to a single geom!
        if project.no_fly_zones:
            no_fly_geoms = json.dumps(project.no_fly_zones["features"][0]["geometry"])
            model_dump.update(
                {
                    "no_fly_zones": no_fly_geoms,
                }
            )

        async with db.cursor() as cur:
            await cur.execute(sql, model_dump)
            new_project_id = await cur.fetchone()

            if not new_project_id:
                msg = f"Unknown SQL error for data: {model_dump}"
                log.warning(f"User ({user_id}) failed project creation: {msg}")
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=msg
                )

            return new_project_id[0]

    @staticmethod
    async def delete(db: Connection, project_id: uuid.UUID) -> uuid.UUID:
        """Delete a single project."""
        sql = """
            WITH deleted_project AS (
                DELETE FROM projects
                WHERE id = %(project_id)s
                RETURNING id
            ), deleted_tasks AS (
                DELETE FROM tasks
                WHERE project_id = %(project_id)s
                RETURNING project_id
            ), deleted_task_events AS (
                DELETE FROM task_events
                WHERE project_id = %(project_id)s
                RETURNING project_id
            )
            SELECT id FROM deleted_project
        """

        async with db.cursor() as cur:
            await cur.execute(sql, {"project_id": project_id})
            deleted_project_id = await cur.fetchone()

            if not deleted_project_id:
                log.warning(f"Failed to delete project ({project_id})")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

            return deleted_project_id[0]


class ProjectOut(BaseModel):
    """Base project model."""

    id: uuid.UUID
    slug: Optional[str] = None
    name: str
    description: str
    per_task_instructions: Optional[str] = None
    outline: Polygon
    task_count: int = 0
    tasks: Optional[list[TaskOut]] = []


class PresignedUrlRequest(BaseModel):
    project_id: uuid.UUID
    task_id: uuid.UUID
    image_name: List[str]
    expiry: int  # Expiry time in hours
