# Regras obrigatórias do projeto

## Produto

Esta aplicação apresenta observações calculadas a partir de dados geográficos públicos.

Nunca deve inferir:
- propriedade jurídica;
- capacidade de construção;
- acesso legal;
- disponibilidade ou potabilidade de água;
- licenciamento;
- legalidade de construções;
- valor de mercado.

Cada resultado deve conter:
- autoridade;
- nome do dataset;
- versão;
- data de obtenção;
- método de cálculo;
- confiança;
- limitações.

## Geoespacial

- Entrada web: EPSG:4326.
- Cálculos métricos no continente: EPSG:3763.
- Nunca calcular área ou distância diretamente em EPSG:4326.
- Validar e reparar geometrias antes da análise.
- Preservar versões importadas.
- Nunca substituir uma camada ativa antes da validação.

## Desenvolvimento

- Implementar módulos pequenos.
- Não adicionar IA ao motor de cálculo.
- Não fazer scraping sem licença explícita.
- Preferir downloads oficiais, OGC API, WFS e ArcGIS FeatureServer.
- Adicionar testes espaciais para interseção, não interseção, fronteira, CRS e ausência de dados.

## Critério de conclusão

Uma tarefa só está concluída quando:
- os testes passam;
- a proveniência é guardada;
- dados ausentes são explícitos;
- não existe conclusão legal;
- os resultados correspondem aos casos de referência.
