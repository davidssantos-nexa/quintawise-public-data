from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.datasets import relation_exists


def analyse_terrain(db: Session, metric_wkt: str) -> dict | None:
    # Raster tables are created by raster2pgsql. Tiles retain SRID 3763.
    if not relation_exists(db, "public.terrain_elevation"):
        return None

    row = (
        db.execute(
            text(
                """
            WITH property AS (
                SELECT ST_GeomFromText(:metric_wkt, 3763) AS geometry
            ),
            clipped AS (
                SELECT ST_Clip(r.rast, p.geometry, TRUE) AS rast
                FROM public.terrain_elevation r
                CROSS JOIN property p
                WHERE ST_Intersects(r.rast, p.geometry)
            ),
            summary AS (
                SELECT (ST_SummaryStatsAgg(rast, 1, TRUE)).*
                FROM clipped
            )
            SELECT min, mean, max FROM summary
            """
            ),
            {"metric_wkt": metric_wkt},
        )
        .mappings()
        .first()
    )

    if not row or row["mean"] is None:
        return None

    return {
        "elevation_min_m": round(float(row["min"]), 1),
        "elevation_mean_m": round(float(row["mean"]), 1),
        "elevation_max_m": round(float(row["max"]), 1),
        "slope_mean_deg": None,
        "slope_p90_deg": None,
    }
