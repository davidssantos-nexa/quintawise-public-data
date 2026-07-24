from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Geometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: list[Any]


class AnalysisRequest(BaseModel):
    geometry: Geometry
    name: str | None = None


class Provenance(BaseModel):
    authority: str
    dataset: str
    version: str
    acquired_at: datetime | None = None
    source_url: str | None = None
    license: str | None = None
    checksum_sha256: str | None = None
    method: str
    confidence: Literal["high", "medium", "low"]
    limitations: list[str] = Field(default_factory=list)


class AdministrativeIntersection(BaseModel):
    parish_code: str | None = None
    parish_name: str
    municipality_name: str
    district_name: str | None = None
    area_m2: float
    percentage: float


class ClassIntersection(BaseModel):
    code: str | None = None
    label: str
    area_m2: float
    percentage: float


class DistanceObservation(BaseModel):
    label: str
    distance_m: float
    intersects: bool


class TerrainObservation(BaseModel):
    elevation_min_m: float | None = None
    elevation_mean_m: float | None = None
    elevation_max_m: float | None = None
    slope_mean_deg: float | None = None
    slope_p90_deg: float | None = None


class ModuleStatus(BaseModel):
    status: Literal["available", "unavailable", "partial"]
    dataset_slug: str
    message: str | None = None


class AnalysisResponse(BaseModel):
    id: str
    name: str | None = None
    area_m2: float = Field(ge=0)
    geometry_valid: bool
    status: str
    administrative: list[AdministrativeIntersection] = Field(default_factory=list)
    land_cover: list[ClassIntersection] = Field(default_factory=list)
    fire_hazard: list[ClassIntersection] = Field(default_factory=list)
    water: list[DistanceObservation] = Field(default_factory=list)
    terrain: TerrainObservation | None = None
    modules: dict[str, ModuleStatus] = Field(default_factory=dict)
    provenance: list[Provenance] = Field(default_factory=list)
    limitations: list[str]


class CompareRequest(BaseModel):
    analysis_ids: list[str] = Field(min_length=2, max_length=3)
