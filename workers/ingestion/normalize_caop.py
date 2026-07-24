import os
import re

import psycopg2
from psycopg2 import sql

CONNECTION = {
    "host": os.environ["PGHOST"],
    "port": os.environ.get("PGPORT", "5432"),
    "dbname": os.environ["PGDATABASE"],
    "user": os.environ["PGUSER"],
    "password": os.environ["PGPASSWORD"],
}

FIELD_CANDIDATES = {
    "parish_code": ["dtmnfr", "dicofre", "codigo", "code", "nationalcode"],
    "parish_name": ["freguesia", "freguesia_name", "name", "nationallevelname"],
    "municipality_name": ["municipio", "concelho", "municipality", "municipality_name"],
    "district_name": ["distrito", "district", "district_name"],
}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def choose(
    columns: list[str], candidates: list[str], required: bool = True
) -> str | None:
    by_normalized = {normalized(col): col for col in columns}
    for candidate in candidates:
        key = normalized(candidate)
        if key in by_normalized:
            return by_normalized[key]
    for candidate in candidates:
        key = normalized(candidate)
        for norm, original in by_normalized.items():
            if key in norm or norm in key:
                return original
    if required:
        raise RuntimeError(
            f"Campo obrigatório não encontrado. Candidatos={candidates}; colunas={columns}"
        )
    return None


with (
    psycopg2.connect(**CONNECTION) as conn,
    conn.cursor() as cur,
):
    cur.execute(
        """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public'
              AND table_name='caop_freguesias_raw_import'
            ORDER BY ordinal_position
            """
    )
    columns = [row[0] for row in cur.fetchall()]
    if not columns:
        raise RuntimeError("Tabela importada não encontrada.")

    geometry_column = choose(columns, ["geometry", "geom", "wkb_geometry"])
    parish_code = choose(columns, FIELD_CANDIDATES["parish_code"], required=False)
    parish_name = choose(columns, FIELD_CANDIDATES["parish_name"])
    municipality_name = choose(columns, FIELD_CANDIDATES["municipality_name"])
    district_name = choose(columns, FIELD_CANDIDATES["district_name"], required=False)

    parish_code_expr = (
        sql.Identifier(parish_code) if parish_code else sql.SQL("NULL::text")
    )
    district_expr = (
        sql.Identifier(district_name) if district_name else sql.SQL("NULL::text")
    )

    cur.execute("DROP TABLE IF EXISTS public.caop_freguesias_next")
    query = sql.SQL(
        """
            CREATE TABLE public.caop_freguesias_next AS
            SELECT
                row_number() OVER ()::bigint AS id,
                {parish_code}::text AS parish_code,
                {parish_name}::text AS parish_name,
                {municipality_name}::text AS municipality_name,
                {district_name}::text AS district_name,
                ST_Multi(ST_CollectionExtract(ST_MakeValid({geometry}), 3))
                    ::geometry(MultiPolygon, 3763) AS geometry
            FROM public.caop_freguesias_raw_import
            WHERE {geometry} IS NOT NULL
            """
    ).format(
        parish_code=parish_code_expr,
        parish_name=sql.Identifier(parish_name),
        municipality_name=sql.Identifier(municipality_name),
        district_name=district_expr,
        geometry=sql.Identifier(geometry_column),
    )
    cur.execute(query)
    cur.execute("DELETE FROM public.caop_freguesias_next WHERE ST_IsEmpty(geometry)")
    cur.execute("ALTER TABLE public.caop_freguesias_next ADD PRIMARY KEY (id)")
    cur.execute(
        "CREATE INDEX caop_freguesias_next_geometry_gix "
        "ON public.caop_freguesias_next USING GIST (geometry)"
    )

    cur.execute("SELECT COUNT(*) FROM public.caop_freguesias_next")
    count = cur.fetchone()[0]
    if count < 2000:
        raise RuntimeError(f"Validação falhou: apenas {count} freguesias importadas.")

    cur.execute(
        """
            SELECT COUNT(*)
            FROM public.caop_freguesias_next
            WHERE parish_name IS NULL OR municipality_name IS NULL
            """
    )
    incomplete = cur.fetchone()[0]
    if incomplete:
        raise RuntimeError(
            f"Validação falhou: {incomplete} registos sem nome obrigatório."
        )

    cur.execute("DROP TABLE IF EXISTS public.caop_freguesias_previous")
    cur.execute(
        """
            DO $$
            BEGIN
              IF to_regclass('public.caop_freguesias') IS NOT NULL THEN
                ALTER TABLE public.caop_freguesias
                RENAME TO caop_freguesias_previous;
              END IF;
            END $$;
            """
    )
    cur.execute("ALTER TABLE public.caop_freguesias_next RENAME TO caop_freguesias")
    cur.execute("DROP TABLE IF EXISTS public.caop_freguesias_raw_import")

    cur.execute(
        """
            UPDATE datasets
            SET active = TRUE,
                downloaded_at = now(),
                version = 'CAOP2025',
                checksum = %s,
                source_url = %s,
                license = %s,
                notes = 'GeoPackage oficial importado, normalizado e validado.'
            WHERE slug = 'caop-2025'
            """,
        (
            os.environ["SOURCE_CHECKSUM_SHA256"],
            os.environ["SOURCE_URL"],
            os.environ["SOURCE_LICENSE"],
        ),
    )
    cur.execute(
        """
            UPDATE dataset_versions
            SET active = FALSE
            WHERE dataset_id = (
                SELECT id FROM datasets WHERE slug = 'caop-2025'
            )
            """
    )
    cur.execute(
        """
            INSERT INTO dataset_versions (
                dataset_id,
                version,
                downloaded_at,
                checksum_sha256,
                source_url,
                license,
                active,
                validation,
                limitations
            )
            SELECT
                id,
                'CAOP2025',
                now(),
                %s,
                %s,
                %s,
                TRUE,
                jsonb_build_object(
                    'row_count', %s,
                    'required_names_missing', 0,
                    'geometry_repaired', TRUE,
                    'target_crs', 'EPSG:3763'
                ),
                jsonb_build_array(
                    'A localização administrativa depende do polígono desenhado pelo utilizador.',
                    'A camada não confirma limites cadastrais nem propriedade.'
                )
            FROM datasets
            WHERE slug = 'caop-2025'
            ON CONFLICT (
                dataset_id,
                version,
                (COALESCE(checksum_sha256, ''))
            )
            DO UPDATE SET
                downloaded_at = EXCLUDED.downloaded_at,
                source_url = EXCLUDED.source_url,
                license = EXCLUDED.license,
                active = TRUE,
                validation = EXCLUDED.validation,
                limitations = EXCLUDED.limitations
            """,
        (
            os.environ["SOURCE_CHECKSUM_SHA256"],
            os.environ["SOURCE_URL"],
            os.environ["SOURCE_LICENSE"],
            count,
        ),
    )

    print(f"Registos normalizados: {count}")
