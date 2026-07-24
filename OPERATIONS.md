# Operações e qualidade

Cada dataset exige:
- página oficial e licença;
- URL de download confirmado, versão e checksum SHA-256;
- CRS confirmado;
- validação de cobertura e contagem;
- geometrias válidas;
- testes de interseção, não interseção e fronteira;
- comparação visual com o portal oficial;
- rollback testado.

O registo imutável de cada importação fica em `dataset_versions`. Apenas uma
versão por dataset pode estar ativa. Nunca se elimina o registo de uma versão
substituída.

Se uma fonte falhar:
- desativar apenas o módulo;
- apresentar unavailable;
- manter os restantes módulos;
- nunca usar silenciosamente uma versão desconhecida.

## Checklist de release

- migrations aplicadas duas vezes sem alterações inesperadas;
- testes API e build web passam;
- `/health` responde sem consultar a base;
- `/ready` confirma PostgreSQL e PostGIS;
- CORS contém apenas origens conhecidas;
- nenhum segredo está no repositório;
- cada módulo sem dados aparece como `unavailable`;
- relatório e API apresentam proveniência e limitações;
- comparação visual concluída contra o portal oficial.
