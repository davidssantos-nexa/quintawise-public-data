# QuintaWise Public Land Intelligence

QuintaWise transforma informação territorial pública portuguesa num retrato factual, rastreável e comparável de terrenos e propriedades rurais.

O produto apresenta observações calculadas sobre camadas públicas. Não conclui
propriedade, edificabilidade, acesso legal, licenciamento, disponibilidade de
água ou valor de mercado.

## Stack

- frontend: Next.js e MapLibre;
- API: FastAPI;
- dados: PostgreSQL 16 e PostGIS 3.4;
- ingestão: GDAL/OGR e importadores versionados;
- deployment preparado: Vercel (web), Render (API) e Neon Postgres/PostGIS.

## Arranque local

```bash
cp .env.example .env
docker compose up --build
```

Web: http://localhost:3000  
API: http://localhost:8000/docs  
Readiness: http://localhost:8000/ready

As migrations SQL são aplicadas automaticamente pela API e registadas com
checksum em `schema_migrations`. Uma migration aplicada nunca deve ser alterada;
deve ser criada uma nova.

## Dados oficiais

`workers/ingestion/source_manifest.json` é o registo de fontes. Um URL de
download só pode ser configurado depois de confirmado numa página oficial.
Enquanto isso, permanece `null` e o módulo aparece como indisponível.

Exemplo de importação, apenas depois de confirmar `CAOP_URL`:

```bash
CAOP_URL="URL_OFICIAL_CONFIRMADO" SOURCE_LICENSE="LICENÇA_CONFIRMADA" \
docker compose --profile ingestion run --rm ingestion /app/import_caop.sh
```

Cada versão importada guarda data de obtenção, checksum SHA-256, validações,
limitações e estado ativo. A ativação da nova versão ocorre apenas depois da
normalização e validação; as versões anteriores permanecem registadas.

## Testes sem Docker

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r apps/api/requirements-dev.txt
PYTHONPATH=apps/api pytest -q apps/api/tests

cd apps/web
npm ci
npm run build
```

Consulte `DEPLOYMENT.md` e `OPERATIONS.md` antes de publicar ou importar dados.
