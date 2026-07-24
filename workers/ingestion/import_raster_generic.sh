#!/usr/bin/env bash
set -euo pipefail

: "${SOURCE_URL:?SOURCE_URL obrigatório}"
: "${TARGET_TABLE:?TARGET_TABLE obrigatório}"
: "${DATASET_SLUG:?DATASET_SLUG obrigatório}"

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
  cp "$ARCHIVE" "$EXTRACT/source.tif"
fi

RASTER="$(find "$EXTRACT" -type f \( -iname '*.tif' -o -iname '*.tiff' \) | head -n 1)"
if [ -z "$RASTER" ]; then
  echo "GeoTIFF não encontrado." >&2
  exit 1
fi

export PGPASSWORD
raster2pgsql -s 3763 -I -C -M -t 256x256 "$RASTER" "public.${TARGET_TABLE}_next" \
  | psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE"

echo "Raster importado para ${TARGET_TABLE}_next; ativação requer validação."
