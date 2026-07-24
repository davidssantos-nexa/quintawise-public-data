ALTER TABLE datasets ADD COLUMN IF NOT EXISTS slug TEXT;
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS notes TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS datasets_slug_idx ON datasets(slug);

INSERT INTO datasets
(slug, name, authority, source_type, source_url, geographic_scope, version, active, notes)
VALUES
('caop-2025', 'Carta Administrativa Oficial de Portugal', 'DGT', 'download/OGC API',
 'https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/caop',
 'Portugal', 'CAOP2025', false,
 'Fonte prioritária para município e freguesia. Importar GeoPackage oficial.'),
('cos-continental', 'Carta de Uso e Ocupação do Solo', 'DGT', 'OGC API/download',
 'https://www.dgterritorio.gov.pt/dados-abertos',
 'Portugal Continental', 'latest-reviewed', false,
 'Usar a versão COS aprovada; não inferir produtividade agrícola.'),
('cadastro-continental', 'Cadastro Predial - Continente', 'DGT', 'OGC API/download',
 'https://www.dgterritorio.gov.pt/dados-abertos',
 'Portugal Continental', 'latest-reviewed', false,
 'Cobertura incompleta. Correspondência cadastral não prova propriedade.'),
('crus-continental', 'Carta do Regime de Uso do Solo', 'DGT', 'OGC API/download',
 'https://www.dgterritorio.gov.pt/dados-abertos',
 'Portugal Continental', 'latest-reviewed', false,
 'Camada agregada; não produz conclusão de edificabilidade.'),
('fire-hazard-2020-2030', 'Carta de Perigosidade de Incêndio Rural', 'ICNF', 'GeoTIFF/WMS',
 'https://geocatalogo.icnf.pt/catalogo_tema5.html',
 'Portugal Continental', '2020-2030', false,
 'Perigosidade estrutural cartografada; não é previsão de incêndio.'),
('hydro-network', 'Rede Hidrográfica GeoCodificada', 'APA', 'catalog/download',
 'https://sniambgeoviewer.apambiente.pt/Geodocs/atom/inspire/downloadservice.html',
 'Portugal Continental', 'published-2006-revised-2015', false,
 'Indica linhas de água cartografadas; não confirma disponibilidade de água.')
ON CONFLICT (slug) DO NOTHING;
