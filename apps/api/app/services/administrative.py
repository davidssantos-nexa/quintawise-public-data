from sqlalchemy import text
from sqlalchemy.orm import Session


def table_exists(db: Session) -> bool:
    return bool(
        db.execute(
            text("SELECT to_regclass('public.caop_freguesias') IS NOT NULL")
        ).scalar()
    )


def analyse_administrative(
    db: Session,
    metric_wkt: str,
    property_area_m2: float,
) -> list[dict]:
    if not table_exists(db):
        return []

    rows = (
        db.execute(
            text(
                """
            WITH property AS (
                SELECT ST_GeomFromText(:metric_wkt, 3763) AS geometry
            )
            SELECT
                parish_code,
                parish_name,
                municipality_name,
                district_name,
                ST_Area(
                    ST_Intersection(ST_MakeValid(c.geometry), p.geometry)
                ) AS area_m2
            FROM public.caop_freguesias c
            CROSS JOIN property p
            WHERE ST_Intersects(c.geometry, p.geometry)
            ORDER BY area_m2 DESC
            """
            ),
            {"metric_wkt": metric_wkt},
        )
        .mappings()
        .all()
    )

    output = []
    for row in rows:
        area = float(row["area_m2"])
        output.append(
            {
                "parish_code": row["parish_code"],
                "parish_name": row["parish_name"],
                "municipality_name": row["municipality_name"],
                "district_name": row["district_name"],
                "area_m2": round(area, 2),
                "percentage": round((area / property_area_m2) * 100, 2),
            }
        )
    return output
