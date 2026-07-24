from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Dataset, DatasetVersion

router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


@router.get("")
def list_datasets(db: DbSession):
    rows = db.query(Dataset).order_by(Dataset.authority, Dataset.name).all()
    output = []
    for row in rows:
        versions = (
            db.query(DatasetVersion)
            .filter(DatasetVersion.dataset_id == row.id)
            .order_by(DatasetVersion.created_at.desc())
            .all()
        )
        output.append(
            {
                "slug": row.slug,
                "name": row.name,
                "authority": row.authority,
                "source_type": row.source_type,
                "notes": row.notes,
                "versions": [
                    {
                        "version": version.version,
                        "published_at": version.published_at,
                        "downloaded_at": version.downloaded_at,
                        "checksum_sha256": version.checksum_sha256,
                        "source_url": version.source_url,
                        "license": version.license,
                        "active": version.active,
                        "validation": version.validation,
                        "limitations": version.limitations,
                    }
                    for version in versions
                ],
            }
        )
    return output
