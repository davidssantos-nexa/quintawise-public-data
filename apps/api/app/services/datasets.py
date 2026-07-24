from sqlalchemy import text
from sqlalchemy.orm import Session


def active_dataset(db: Session, slug: str) -> dict | None:
    row = (
        db.execute(
            text(
                """
            SELECT
                d.slug,
                d.name,
                d.authority,
                v.version,
                v.source_url,
                v.license,
                v.downloaded_at,
                v.checksum_sha256,
                v.limitations,
                d.notes
            FROM datasets d
            JOIN dataset_versions v ON v.dataset_id = d.id
            WHERE d.slug = :slug AND v.active = TRUE
            LIMIT 1
            """
            ),
            {"slug": slug},
        )
        .mappings()
        .first()
    )
    return dict(row) if row else None


def relation_exists(db: Session, relation: str) -> bool:
    return bool(
        db.execute(
            text("SELECT to_regclass(:relation) IS NOT NULL"),
            {"relation": relation},
        ).scalar()
    )
