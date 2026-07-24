#!/usr/bin/env bash
set -euo pipefail

: "${SOURCE_URL:?SOURCE_URL obrigatório}"
: "${TARGET_TABLE:?TARGET_TABLE obrigatório}"
: "${SOURCE_AUTHORITY:?SOURCE_AUTHORITY obrigatório}"
: "${DATASET_SLUG:?DATASET_SLUG obrigatório}"
: "${DATASET_VERSION:?DATASET_VERSION obrigatório}"

WORKDIR="/data/${DATASET_SLUG}"
ARCHIVE="$WORKDIR/source"
EXTRACT="$WORKDIR/extracted"
mkdir -p "$EXTRACT"
rm -rf "$EXTRACT"/*

until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE"; do
  sleep 2
done

curl --fail --location --retry 3 --output "$ARCHIVE" "$SOURCE_URL"

if file "$ARCHIVE" | grep -qi zip; then
  unzip -q -o "$ARCHIVE" -d "$EXTRACT"
else
  cp "$ARCHIVE" "$EXTRACT/source"
fi

SOURCE_FILE="$(find "$EXTRACT" -type f \( -iname '*.gpkg' -o -iname '*.shp' -o -iname '*.geojson' \) | head -n 1)"
if [ -z "$SOURCE_FILE" ]; then
  echo "Não foi encontrado ficheiro vetorial suportado." >&2
  exit 1
fi

CONNECTION="PG:host=$PGHOST port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD"

ogr2ogr \
  -f PostgreSQL "$CONNECTION" "$SOURCE_FILE" \
  -nln "public.${TARGET_TABLE}_raw_import" \
  -lco GEOMETRY_NAME=geometry \
  -nlt PROMOTE_TO_MULTI \
  -t_srs EPSG:3763 \
  -overwrite \
  -makevalid

echo "Importação raw concluída em ${TARGET_TABLE}_raw_import."
echo "É obrigatória normalização específica antes de ativar ${DATASET_SLUG}."
