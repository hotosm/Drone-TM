import logging
import geojson
import requests
import shapely
from datetime import datetime, timezone
from typing import Optional, Union
from geojson_pydantic import Feature, MultiPolygon, Polygon
from geojson_pydantic import FeatureCollection as FeatCol
from geoalchemy2 import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from fastapi import HTTPException
from shapely import wkb


log = logging.getLogger(__name__)


def timestamp():
    """Get the current time.

    Used to insert a current timestamp into Pydantic models.
    """
    return datetime.now(timezone.utc)


def str_to_geojson(
    result: str, properties: Optional[dict] = None, id: Optional[str] = None
) -> Union[Feature, dict]:
    """Convert SQLAlchemy geometry to GeoJSON."""
    if result:
        wkb_data = bytes.fromhex(result)
        geom = wkb.loads(wkb_data)
        geojson = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": properties,
            "id": id,
        }
        return Feature(**geojson)
    return {}


def geometry_to_geojson(
    geometry: WKBElement, properties: Optional[dict] = None, id: Optional[int] = None
) -> Union[Feature, dict]:
    """Convert SQLAlchemy geometry to GeoJSON."""
    if geometry:
        shape = to_shape(geometry)
        geojson = {
            "type": "Feature",
            "geometry": mapping(shape),
            "properties": properties,
            "id": id,
            # "bbox": shape.bounds,
        }
        return Feature(**geojson)
    return {}


def geojson_to_geometry(
    geojson: Union[FeatCol, Feature, MultiPolygon, Polygon],
) -> Optional[WKBElement]:
    """Convert GeoJSON to SQLAlchemy geometry."""
    parsed_geojson = geojson
    if isinstance(geojson, (FeatCol, Feature, MultiPolygon, Polygon)):
        parsed_geojson = parse_and_filter_geojson(
            geojson.model_dump_json(), filter=False
        )

    if not parsed_geojson:
        return None

    features = parsed_geojson.get("features", [])

    if len(features) > 1:
        # TODO code to merge all geoms into multipolygon
        # TODO do not use convex hull
        pass

    geometry = features[0].get("geometry")

    shapely_geom = shape(geometry)

    return from_shape(shapely_geom)


def parse_and_filter_geojson(
    geojson_raw: Union[str, bytes], filter: bool = True
) -> Optional[geojson.FeatureCollection]:
    """Parse geojson string and filter out incomaptible geometries."""
    geojson_parsed = geojson.loads(geojson_raw)

    if isinstance(geojson_parsed, geojson.FeatureCollection):
        log.debug("Already in FeatureCollection format, skipping reparse")
        featcol = geojson_parsed
    elif isinstance(geojson_parsed, geojson.Feature):
        log.debug("Converting Feature to FeatureCollection")
        featcol = geojson.FeatureCollection(features=[geojson_parsed])
    else:
        log.debug("Converting Geometry to FeatureCollection")
        featcol = geojson.FeatureCollection(
            features=[geojson.Feature(geometry=geojson_parsed)]
        )

    # Exit early if no geoms
    if not (features := featcol.get("features", [])):
        return None

    # Strip out GeometryCollection wrappers
    for feat in features:
        geom = feat.get("geometry")
        if (
            geom.get("type") == "GeometryCollection"
            and len(geom.get("geometries")) == 1
        ):
            feat["geometry"] = geom.get("geometries")[0]

    # Return unfiltered featcol
    if not filter:
        return featcol

    # Filter out geoms not matching main type
    geom_type = get_featcol_main_geom_type(featcol)
    features_filtered = [
        feature
        for feature in features
        if feature.get("geometry", {}).get("type", "") == geom_type
    ]

    return geojson.FeatureCollection(features_filtered)


def get_featcol_main_geom_type(featcol: geojson.FeatureCollection) -> str:
    """Get the predominant geometry type in a FeatureCollection."""
    geometry_counts = {"Polygon": 0, "Point": 0, "Polyline": 0}

    for feature in featcol.get("features", []):
        geometry_type = feature.get("geometry", {}).get("type", "")
        if geometry_type in geometry_counts:
            geometry_counts[geometry_type] += 1

    return max(geometry_counts, key=geometry_counts.get)


def read_wkb(wkb: WKBElement):
    """Load a WKBElement and return a shapely geometry."""
    return to_shape(wkb)


def write_wkb(shape):
    """Load shapely geometry and output WKBElement."""
    return from_shape(shape)


def merge_multipolygon(features: Union[Feature, FeatCol, MultiPolygon, Polygon]):
    """Merge multiple Polygons or MultiPolygons into a single Polygon.

    Args:
        features: geojson features to merge.

    Returns:
        A GeoJSON FeatureCollection containing the merged Polygon.
    """
    try:

        def remove_z_dimension(coord):
            """Remove z dimension from geojson."""
            return coord.pop() if len(coord) == 3 else None

        features = parse_featcol(features)

        multi_polygons = []
        # handles both collection or single feature
        features = features.get("features", [features])

        for feature in features:
            list(map(remove_z_dimension, feature["geometry"]["coordinates"][0]))
            polygon = shapely.geometry.shape(feature["geometry"])
            multi_polygons.append(polygon)

        merged_polygon = unary_union(multi_polygons)
        if isinstance(merged_polygon, MultiPolygon):
            merged_polygon = merged_polygon.convex_hull

        merged_geojson = mapping(merged_polygon)
        if merged_geojson["type"] == "MultiPolygon":
            log.error(
                "Resulted GeoJSON contains disjoint Polygons. "
                "Adjacent polygons are preferred."
            )
        return geojson.FeatureCollection([geojson.Feature(geometry=merged_geojson)])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Couldn't merge the multipolygon to polygon: {str(e)}",
        ) from e


def parse_featcol(features: Union[Feature, FeatCol, MultiPolygon, Polygon]):
    """Parse a feature collection or feature into a GeoJSON FeatureCollection.

    Args:
        features: Feature, FeatCol, MultiPolygon, Polygon or dict.

    Returns:
        dict: Parsed GeoJSON FeatureCollection.
    """
    if isinstance(features, dict):
        return features

    feat_col = features.model_dump_json()
    feat_col = geojson.loads(feat_col)
    if isinstance(features, (Polygon, MultiPolygon)):
        feat_col = geojson.FeatureCollection([geojson.Feature(geometry=feat_col)])
    elif isinstance(features, Feature):
        feat_col = geojson.FeatureCollection([feat_col])
    return feat_col


def get_address_from_lat_lon(latitude, longitude):
    """Get address using Nominatim, using lat,lon."""
    base_url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "format": "json",
        "lat": latitude,
        "lon": longitude,
        "zoom": 18,
    }
    headers = {"Accept-Language": "en"}  # Set the language to English

    log.debug("Getting Nominatim address from project centroid")
    response = requests.get(base_url, params=params, headers=headers)
    if (status_code := response.status_code) != 200:
        log.error(f"Getting address string failed: {status_code}")
        return None

    data = response.json()
    log.debug(f"Nominatim response: {data}")

    address = data.get("address", None)
    if not address:
        log.error(f"Getting address string failed: {status_code}")
        return None

    country = address.get("country", "")
    city = address.get("city", "")
    state = address.get("state", "")

    address_str = f"{city},{country}" if city else f"{state},{country}"

    if not address_str or address_str == ",":
        log.error("Getting address string failed")
        return None

    return address_str


def multipolygon_to_polygon(features: Union[Feature, FeatCol, MultiPolygon, Polygon]):
    """Converts a GeoJSON FeatureCollection of MultiPolygons to Polygons.

    Args:
        features : A GeoJSON FeatureCollection containing MultiPolygons/Polygons.

    Returns:
        geojson.FeatureCollection: A GeoJSON FeatureCollection containing Polygons.
    """
    geojson_feature = []
    features = parse_featcol(features)

    # handles both collection or single feature
    features = features.get("features", [features])

    for feature in features:
        properties = feature["properties"]
        geom = shape(feature["geometry"])
        if geom.geom_type == "Polygon":
            geojson_feature.append(
                geojson.Feature(geometry=geom, properties=properties)
            )
        elif geom.geom_type == "MultiPolygon":
            geojson_feature.extend(
                geojson.Feature(geometry=polygon_coords, properties=properties)
                for polygon_coords in geom.geoms
            )

    return geojson.FeatureCollection(geojson_feature)
