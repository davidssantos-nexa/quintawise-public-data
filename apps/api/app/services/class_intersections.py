from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.datasets import relation_exists

ALLOWED_TABLES = {
    "land_cover": "public.land_cover_classes",
    "fire_hazard": "public.fire_hazard_classes",
}


def analyse_class_intersections(
    db: Session,
    module: str,
    metric_wkt: str,
    property_area_m2: float,
) -> list[dict]:
    relation = ALLOWED_TABLES[module]
    if not relation_exists(db, relation):
        return []

    # Table name comes only from the fixed allow-list above.
    query = text(
        f"""
        WITH property AS (
            SELECT ST_GeomFromText(:metric_wkt, 3763) AS geometry
        )
        SELECT
            code,
            label,
            SUM(
                ST_Area(ST_Intersection(ST_MakeValid(c.geometry), p.geometry))
            ) AS area_m2
        FROM {relation} c
        CROSS JOIN property p
        WHERE ST_Intersects(c.geometry, p.geometry)
        GROUP BY code, label
        ORDER BY area_m2 DESC
        """
    )
    rows = db.execute(query, {"metric_wkt": metric_wkt}).mappings().all()

    return [
        {
            "code": row["code"],
            "label": row["label"],
            "area_m2": round(float(row["area_m2"]), 2),
            "percentage": round((float(row["area_m2"]) / property_area_m2) * 100, 2),
        }
        for row in rows
    ]
