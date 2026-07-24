from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.datasets import relation_exists


def analyse_water(db: Session, metric_wkt: str) -> list[dict]:
    relation = "public.hydro_network"
    if not relation_exists(db, relation):
        return []

    row = (
        db.execute(
            text(
                """
            WITH property AS (
                SELECT ST_GeomFromText(:metric_wkt, 3763) AS geometry
            )
            SELECT
                COALESCE(NULLIF(h.name, ''), 'Linha de água cartografada') AS label,
                ST_Distance(h.geometry, p.geometry) AS distance_m,
                ST_Intersects(h.geometry, p.geometry) AS intersects
            FROM public.hydro_network h
            CROSS JOIN property p
            ORDER BY h.geometry <-> p.geometry
            LIMIT 1
            """
            ),
            {"metric_wkt": metric_wkt},
        )
        .mappings()
        .first()
    )

    if not row:
        return []
    return [
        {
            "label": row["label"],
            "distance_m": round(float(row["distance_m"]), 1),
            "intersects": bool(row["intersects"]),
        }
    ]
