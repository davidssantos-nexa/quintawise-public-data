CREATE TABLE IF NOT EXISTS land_cover_classes (
    id BIGSERIAL PRIMARY KEY,
    code TEXT,
    label TEXT NOT NULL,
    geometry geometry(MultiPolygon, 3763) NOT NULL
);
CREATE INDEX IF NOT EXISTS land_cover_classes_geometry_gix
ON land_cover_classes USING GIST (geometry);

CREATE TABLE IF NOT EXISTS fire_hazard_classes (
    id BIGSERIAL PRIMARY KEY,
    code TEXT,
    label TEXT NOT NULL,
    geometry geometry(MultiPolygon, 3763) NOT NULL
);
CREATE INDEX IF NOT EXISTS fire_hazard_classes_geometry_gix
ON fire_hazard_classes USING GIST (geometry);

CREATE TABLE IF NOT EXISTS hydro_network (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    code TEXT,
    geometry geometry(MultiLineString, 3763) NOT NULL
);
CREATE INDEX IF NOT EXISTS hydro_network_geometry_gix
ON hydro_network USING GIST (geometry);

INSERT INTO datasets
(slug, name, authority, source_type, source_url, geographic_scope, version, active, notes)
VALUES
('cos-2023-s2', 'Carta de Uso e Ocupação do Solo 2023 — Série 2', 'DGT',
 'GeoPackage/OGC', 'https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/SMOS-CLMS',
 'Portugal Continental', 'COS2023v1 Série 2', false,
 'Importar apenas após mapear os códigos para a nomenclatura oficial.'),
('terrain-dtm', 'Modelo Digital do Terreno LiDAR', 'DGT',
 'GeoTIFF', 'https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-topografica/modelos-digitais',
 'Portugal Continental', 'LiDAR 2024-2025', false,
 'Coleção segmentada; importar tiles necessários e manter índice de cobertura.')
ON CONFLICT (slug) DO NOTHING;
