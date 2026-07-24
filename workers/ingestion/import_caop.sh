#!/usr/bin/env bash
set -euo pipefail

: "${CAOP_URL:?Defina CAOP_URL apenas com um URL de download oficial confirmado da DGT/SNIG.}"
: "${SOURCE_LICENSE:?Defina SOURCE_LICENSE com a licença confirmada na fonte oficial.}"
WORKDIR="/data/caop2025"
ZIP_PATH="$WORKDIR/caop2025.zip"
EXTRACT_DIR="$WORKDIR/extracted"

mkdir -p "$EXTRACT_DIR"

echo "A aguardar pelo PostgreSQL..."
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE"; do
  sleep 2
done

if [ ! -s "$ZIP_PATH" ]; then
  echo "A descarregar CAOP2025 da DGT..."
  curl --fail --location --retry 3 --output "$ZIP_PATH" "$CAOP_URL"
fi

export SOURCE_CHECKSUM_SHA256
SOURCE_CHECKSUM_SHA256="$(sha256sum "$ZIP_PATH" | awk '{print $1}')"
export SOURCE_URL="$CAOP_URL"
export SOURCE_LICENSE

rm -rf "$EXTRACT_DIR"/*
unzip -q -o "$ZIP_PATH" -d "$EXTRACT_DIR"

GPKG_PATH="$(find "$EXTRACT_DIR" -type f -iname '*.gpkg' | head -n 1)"
if [ -z "$GPKG_PATH" ]; then
  echo "GeoPackage não encontrado." >&2
  exit 1
fi

echo "GeoPackage: $GPKG_PATH"

# Descobre automaticamente a camada poligonal de freguesias.
LAYER="$(
  ogrinfo -ro -so "$GPKG_PATH" 2>/dev/null \
  | sed -n 's/^[0-9][0-9]*: \([^ (]*\).*/\1/p' \
  | grep -Ei 'freg|administrativeunit.*parish|area.*freg' \
  | head -n 1
)"

if [ -z "$LAYER" ]; then
  echo "Não foi possível identificar a camada de freguesias." >&2
  echo "Camadas disponíveis:" >&2
  ogrinfo -ro -so "$GPKG_PATH" >&2
  exit 1
fi

echo "Camada selecionada: $LAYER"

CONNECTION="PG:host=$PGHOST port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD"

ogr2ogr \
  -f PostgreSQL "$CONNECTION" "$GPKG_PATH" "$LAYER" \
  -nln public.caop_freguesias_raw_import \
  -lco GEOMETRY_NAME=geometry \
  -lco FID=id \
  -nlt PROMOTE_TO_MULTI \
  -t_srs EPSG:3763 \
  -overwrite \
  -makevalid

python3 /app/normalize_caop.py

echo "CAOP2025 importada e validada."
