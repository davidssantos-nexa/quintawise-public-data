from dataclasses import dataclass
from math import isfinite

from pyproj import Transformer
from shapely.errors import ShapelyError
from shapely.geometry import Polygon, shape
from shapely.ops import transform
from shapely.validation import make_valid


@dataclass(frozen=True)
class GeometryAnalysis:
    input_geometry: Polygon
    metric_geometry: Polygon
    area_m2: float


def analyse_polygon(geojson_geometry: dict) -> GeometryAnalysis:
    coordinates = geojson_geometry.get("coordinates", [])
    vertex_count = sum(len(ring) for ring in coordinates if isinstance(ring, list))
    if vertex_count > 10_000:
        raise ValueError("O polígono excede o limite de 10 000 vértices.")

    try:
        geom = shape(geojson_geometry)
    except (KeyError, TypeError, ValueError, ShapelyError) as exc:
        raise ValueError("A geometria GeoJSON é inválida.") from exc
    if geom.geom_type != "Polygon":
        raise ValueError("A geometria tem de ser um Polygon.")

    geom = make_valid(geom)
    if geom.geom_type != "Polygon":
        raise ValueError("A geometria não pôde ser reparada como Polygon.")

    if geom.is_empty:
        raise ValueError("A geometria está vazia.")

    minx, miny, maxx, maxy = geom.bounds
    if not all(isfinite(value) for value in geom.bounds):
        raise ValueError("A geometria contém coordenadas não finitas.")
    # Limite aproximado para Portugal continental; serve apenas como validação inicial.
    if not (-9.7 <= minx <= maxx <= -6.0 and 36.8 <= miny <= maxy <= 42.3):
        raise ValueError("O polígono não parece estar em Portugal continental.")

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3763", always_xy=True)
    metric = transform(transformer.transform, geom)
    if metric.is_empty or not metric.is_valid:
        raise ValueError("A geometria métrica resultante é inválida.")
    area = float(metric.area)

    if area < 10:
        raise ValueError("A área é demasiado pequena.")
    if area > 100_000_000:
        raise ValueError("A área excede o limite permitido para o MVP.")

    return GeometryAnalysis(
        input_geometry=geom,
        metric_geometry=metric,
        area_m2=area,
    )
