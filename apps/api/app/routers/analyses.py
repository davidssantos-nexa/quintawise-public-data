from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from geoalchemy2.shape import from_shape
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Analysis
from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    CompareRequest,
    ModuleStatus,
    Provenance,
)
from app.services.administrative import analyse_administrative
from app.services.class_intersections import analyse_class_intersections
from app.services.datasets import active_dataset
from app.services.geometry import analyse_polygon
from app.services.reporting import render_report_html
from app.services.terrain import analyse_terrain
from app.services.water import analyse_water

router = APIRouter(prefix="/analyses", tags=["analyses"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def module_status(source, slug, available, empty_message):
    if not source:
        return ModuleStatus(
            status="unavailable",
            dataset_slug=slug,
            message="Dataset ainda não importado e validado.",
        ), None
    if not available:
        return ModuleStatus(
            status="partial", dataset_slug=slug, message=empty_message
        ), source
    return ModuleStatus(status="available", dataset_slug=slug, message=None), source


@router.post("", response_model=AnalysisResponse)
def create_analysis(payload: AnalysisRequest, db: DbSession):
    try:
        geometry = analyse_polygon(payload.geometry.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    wkt = geometry.metric_geometry.wkt
    sources = {
        "administrative": active_dataset(db, "caop-2025"),
        "land_cover": active_dataset(db, "cos-2023-s2"),
        "fire_hazard": active_dataset(db, "fire-hazard-2020-2030"),
        "water": active_dataset(db, "hydro-network"),
        "terrain": active_dataset(db, "terrain-dtm"),
    }
    administrative = (
        analyse_administrative(db, wkt, geometry.area_m2)
        if sources["administrative"]
        else []
    )
    land_cover = (
        analyse_class_intersections(db, "land_cover", wkt, geometry.area_m2)
        if sources["land_cover"]
        else []
    )
    fire_hazard = (
        analyse_class_intersections(db, "fire_hazard", wkt, geometry.area_m2)
        if sources["fire_hazard"]
        else []
    )
    water = analyse_water(db, wkt) if sources["water"] else []
    terrain = analyse_terrain(db, wkt) if sources["terrain"] else None

    modules = {}
    provenance = [
        Provenance(
            authority="QuintaWise",
            dataset="User supplied geometry",
            version="input",
            acquired_at=datetime.now(timezone.utc),
            method="Validation and EPSG:4326 → EPSG:3763 transformation",
            confidence="high",
            limitations=[
                "O limite foi desenhado pelo utilizador e não confirma limites cadastrais."
            ],
        )
    ]
    configs = [
        (
            "administrative",
            "caop-2025",
            administrative,
            "Sem interseção administrativa encontrada.",
        ),
        (
            "land_cover",
            "cos-2023-s2",
            land_cover,
            "Sem classes de uso do solo encontradas.",
        ),
        (
            "fire_hazard",
            "fire-hazard-2020-2030",
            fire_hazard,
            "Sem cobertura de perigosidade encontrada.",
        ),
        (
            "water",
            "hydro-network",
            water,
            "Sem linha de água encontrada na cobertura importada.",
        ),
        ("terrain", "terrain-dtm", terrain, "Sem cobertura altimétrica encontrada."),
    ]
    methods = {
        "administrative": "Valid polygon intersection in EPSG:3763",
        "land_cover": "Valid polygon intersection and area aggregation in EPSG:3763",
        "fire_hazard": "Valid polygon intersection and area aggregation in EPSG:3763",
        "water": "Nearest-feature metric distance and intersection in EPSG:3763",
        "terrain": "Raster clipping and summary statistics in EPSG:3763",
    }
    for key, slug, value, message in configs:
        status, source = module_status(sources[key], slug, bool(value), message)
        modules[key] = status
        if source:
            provenance.append(
                Provenance(
                    authority=source["authority"],
                    dataset=source["name"],
                    version=source["version"],
                    acquired_at=source["downloaded_at"],
                    source_url=source["source_url"],
                    license=source["license"],
                    checksum_sha256=source["checksum_sha256"],
                    method=methods[key],
                    confidence="high" if value else "low",
                    limitations=source["limitations"] or [],
                )
            )

    limitations = [
        "O polígono é fornecido pelo utilizador e não confirma limites cadastrais.",
        "Os resultados descrevem camadas públicas; não constituem parecer jurídico, urbanístico ou técnico.",
        "A ausência de interseção não prova a ausência material ou legal do fenómeno.",
    ]

    snapshot = {
        "name": payload.name,
        "area_m2": round(geometry.area_m2, 2),
        "administrative": administrative,
        "land_cover": land_cover,
        "fire_hazard": fire_hazard,
        "water": water,
        "terrain": terrain,
        "modules": {k: v.model_dump() for k, v in modules.items()},
        "provenance": [x.model_dump(mode="json") for x in provenance],
        "limitations": limitations,
    }

    record = Analysis(
        name=payload.name,
        input_geometry=from_shape(geometry.input_geometry, srid=4326),
        metric_geometry=from_shape(geometry.metric_geometry, srid=3763),
        area_m2=geometry.area_m2,
        status="completed",
        snapshot=snapshot,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return AnalysisResponse(
        id=str(record.id),
        name=payload.name,
        area_m2=snapshot["area_m2"],
        geometry_valid=True,
        status=record.status,
        administrative=administrative,
        land_cover=land_cover,
        fire_hazard=fire_hazard,
        water=water,
        terrain=terrain,
        modules=modules,
        provenance=provenance,
        limitations=limitations,
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: UUID, db: DbSession):
    row = db.get(Analysis, analysis_id)
    if not row or not row.snapshot:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return AnalysisResponse(
        id=str(row.id),
        name=row.name,
        geometry_valid=True,
        status=row.status,
        **row.snapshot,
    )


@router.get("/{analysis_id}/report", response_class=HTMLResponse)
def get_report(analysis_id: UUID, db: DbSession):
    row = db.get(Analysis, analysis_id)
    if not row or not row.snapshot:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return HTMLResponse(render_report_html(row.snapshot))


@router.post("/compare")
def compare_analyses(payload: CompareRequest, db: DbSession):
    output = []
    for index, raw_id in enumerate(payload.analysis_ids):
        try:
            uid = UUID(raw_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=422, detail=f"ID inválido: {raw_id}"
            ) from exc
        row = db.get(Analysis, uid)
        if not row or not row.snapshot:
            raise HTTPException(
                status_code=404, detail=f"Análise não encontrada: {raw_id}"
            )
        output.append(
            {
                "id": str(row.id),
                "name": row.name or f"Terreno {index + 1}",
                "area_m2": row.area_m2,
                "administrative": row.snapshot.get("administrative", []),
                "land_cover": row.snapshot.get("land_cover", []),
                "fire_hazard": row.snapshot.get("fire_hazard", []),
                "water": row.snapshot.get("water", []),
                "terrain": row.snapshot.get("terrain"),
            }
        )
    return {"analyses": output}
