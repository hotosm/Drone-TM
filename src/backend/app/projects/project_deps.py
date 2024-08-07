"""Dependencies for Project endpoints."""

import json
from uuid import UUID
from typing import Annotated
from loguru import logger as log
from fastapi import Depends, HTTPException, Path, File, UploadFile
from psycopg import Connection
from geojson import FeatureCollection

from app.db import database
from app.models.enums import HTTPStatus
from app.projects.project_schemas import DbProject
from app.utils import geojson_to_featcol


async def get_project_by_id(
    project_id: Annotated[
        UUID,
        Path(
            description="The project ID in UUID format.",
        ),
    ],
    db: Annotated[Connection, Depends(database.get_db)],
) -> DbProject:
    """Get a single project by id."""
    try:
        return await DbProject.one(db, project_id)
    except KeyError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND) from e


async def geojson_upload(
    geojson: Annotated[
        UploadFile,
        File(
            description="A GeoJSON file.",
        ),
    ],
) -> FeatureCollection:
    """
    Normalise a geojson upload to a FeatureCollection.

    MultiPolygons will be exploded into Polygon features.
    """
    log.debug("Reading geojson data from uploaded file")
    bytes_data = await geojson.read()

    try:
        geojson_data = json.loads(bytes_data)  #
    except json.decoder.JSONDecodeError as e:
        msg = "Failed to read uploaded GeoJSON file. Is it valid?"
        log.warning(msg)
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=msg
        ) from e

    featcol = geojson_to_featcol(geojson_data)
    if not isinstance(featcol, FeatureCollection):
        msg = "Uploaded GeoJSON could not be parsed to FeatureCollection"
        log.warning(msg)
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=msg)

    return featcol
