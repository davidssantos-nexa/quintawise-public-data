# Deployment gratuito

Arquitetura preparada:

- web: Vercel Hobby, com root directory `apps/web`;
- API: Render Free Web Service, definido em `render.yaml`;
- base: Neon Free Postgres, com a extensão PostGIS ativada.

Estas contas externas e a ligação do repositório têm de ser autorizadas pelo
proprietário. Não existem credenciais no código.

## 1. Base de dados

1. Criar um projeto Neon.
2. Executar `CREATE EXTENSION IF NOT EXISTS postgis;`.
3. Copiar a connection string pooled e trocar o prefixo por
   `postgresql+psycopg://`.
4. Guardá-la como `DATABASE_URL` no Render.

A API executa as migrations checksummed no arranque. Confirmar `/ready` antes de
qualquer ingestão. O plano gratuito é adequado ao MVP e não é garantia de
capacidade para rasters nacionais ou tráfego de produção.

## 2. API

1. No Render, criar um Blueprint a partir deste repositório.
2. Definir `DATABASE_URL`.
3. Definir temporariamente `CORS_ORIGINS` com o domínio Vercel final.
4. Confirmar `/health`, `/ready` e `/docs`.

O serviço gratuito pode suspender por inatividade e ter cold start. O
`render.yaml` não cria uma base Render para evitar assumir que existe uma opção
PostGIS gratuita permanente.

## 3. Frontend

1. Importar o repositório na Vercel.
2. Definir root directory como `apps/web`.
3. Definir `NEXT_PUBLIC_API_URL` com o URL HTTPS da API Render.
4. Fazer novo deployment e atualizar `CORS_ORIGINS` na API com o URL final.

## 4. Dados

1. Resolver o URL de download apenas através da página oficial indicada no
   manifesto.
2. Confirmar licença, versão e CRS.
3. Importar para uma tabela temporária.
4. Validar contagem, cobertura, geometrias e checksum.
5. Ativar a versão só após os testes de referência.

Domínio próprio, pagamentos e planos pagos estão fora deste deployment MVP.
