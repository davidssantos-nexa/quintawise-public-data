import uuid

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    authority = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_url = Column(Text)
    license = Column(Text)
    geographic_scope = Column(String)
    published_at = Column(Date)
    downloaded_at = Column(DateTime(timezone=True))
    version = Column(String, nullable=False)
    checksum = Column(String)
    active = Column(Boolean, nullable=False, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(String, nullable=False)
    published_at = Column(Date)
    downloaded_at = Column(DateTime(timezone=True))
    checksum_sha256 = Column(String)
    source_url = Column(Text)
    license = Column(Text)
    active = Column(Boolean, nullable=False, default=False)
    validation = Column(JSONB, nullable=False, default=dict)
    limitations = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    input_geometry = Column(Geometry("POLYGON", srid=4326), nullable=False)
    metric_geometry = Column(Geometry("POLYGON", srid=3763), nullable=False)
    area_m2 = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="completed")
    snapshot = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"))
    indicator = Column(String, nullable=False)
    value_numeric = Column(Float)
    value_text = Column(Text)
    unit = Column(String)
    confidence = Column(String, nullable=False)
    method = Column(Text, nullable=False)
    limitations = Column(JSONB, nullable=False, default=list)
    evidence = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
