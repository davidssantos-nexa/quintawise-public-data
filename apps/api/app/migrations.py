"""Apply immutable, checksummed SQL migrations in filename order."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from sqlalchemy import text

from app.db import engine


def _migration_dir() -> Path:
    configured = os.getenv("MIGRATIONS_DIR")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[3] / "infrastructure" / "sql"


def apply_migrations() -> list[str]:
    directory = _migration_dir()
    files = sorted(directory.glob("[0-9][0-9][0-9]_*.sql"))
    if not files:
        raise RuntimeError(f"Não foram encontradas migrations SQL em {directory}.")

    applied_now: list[str] = []
    with engine.begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(78231944)"))
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    checksum_sha256 TEXT NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        )
        applied = dict(
            connection.execute(
                text("SELECT version, checksum_sha256 FROM schema_migrations")
            ).all()
        )

        for path in files:
            version = path.name
            sql = path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
            previous = applied.get(version)
            if previous:
                if previous != checksum:
                    raise RuntimeError(
                        f"A migration aplicada {version} foi alterada; "
                        "crie uma nova migration."
                    )
                continue

            driver_connection = connection.connection.driver_connection
            with driver_connection.cursor() as cursor:
                # Psycopg's simple-query protocol supports multi-statement files.
                cursor.execute(sql, prepare=False)
            connection.execute(
                text(
                    """
                    INSERT INTO schema_migrations (version, checksum_sha256)
                    VALUES (:version, :checksum)
                    """
                ),
                {"version": version, "checksum": checksum},
            )
            applied_now.append(version)

    return applied_now


if __name__ == "__main__":
    migrations = apply_migrations()
    if migrations:
        print("Migrations aplicadas: " + ", ".join(migrations))
    else:
        print("Base de dados já está atualizada.")
