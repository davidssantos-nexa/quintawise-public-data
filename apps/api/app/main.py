from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.db import engine
from app.routers.analyses import router as analyses_router
from app.routers.datasets import router as datasets_router

app = FastAPI(title="QuintaWise Public Data API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyses_router)
app.include_router(datasets_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/ready")
def ready(response: Response):
    database = False
    postgis = False
    try:
        with engine.connect() as connection:
            database = bool(connection.execute(text("SELECT 1")).scalar())
            postgis = bool(
                connection.execute(
                    text("SELECT postgis_version() IS NOT NULL")
                ).scalar()
            )
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    if not (database and postgis):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if database and postgis else "not_ready",
        "database": database,
        "postgis": postgis,
    }
