# Evidências da coleta histórica de BTCUSDT

Primeira entrega de I01, vinculada ao D01, ao fluxo F01 e à cobertura
parcial de G0. A amostra usa candles públicos fechados de cinco minutos,
com uma linha por mercado e horário de abertura no dia UTC de 10/11/2025.
A coleta foi executada em 11/11/2026 com a política TRAINING e LIVE
indisponível. [Fonte pública da Binance](https://github.com/binance/binance-public-data)

| Mercado | Recebidos e esperados | Lacunas | Aberturas duplicadas | Timestamp de origem |
|---|---:|---:|---:|---|
| Spot | 288 de 288 | 0 | 0 | Microssegundos |
| USDⓈ-M Futures | 288 de 288 | 0 | 0 | Milissegundos |

Os dois conjuntos passaram na conferência de ordem, horários de abertura
e fechamento, campos obrigatórios, limites de OHLCV e contagem de
negociações. Ambos começam às 00:00 UTC e terminam com a última janela
encerrada à meia-noite UTC do dia seguinte.

## Rastreabilidade

Os ZIPs conferiram com os checksums publicados pela fonte. O coletor
preservou o ZIP original e gravou um CSV normalizado e um manifesto
por execução. Os arquivos estão em `data/market-history/`, no checkout
local, e o Git versiona o coletor, os testes e esta evidência.

| Mercado | ID da coleta | SHA-256 do ZIP | SHA-256 do CSV |
|---|---|---|---|
| Spot | `f7b25827396548cca4b3193387b4b6f5` | `31a468ebfb250a9977be3f5a29d3cfca3e64c398b972ddd495330d71cbfbeb09` | `d4310a9bdf7c954776012c5f50c19ddee339080a317345c420b7d700ecb22ef1` |
| USDⓈ-M Futures | `a5efd3ca4bec49bcba3e3e4984aed7ff` | `1ecdaad48f291575e2ac107e13183b692dc230101068f85a59340424401c0b23` | `fba3d03334b02465d36863819b192e2fb231c707034ddb04222e74b08bf9d920` |

## Verificações executadas

- `uv sync --locked`, Ruff, mypy e `uv build --no-sources` passaram.
- `uv run --no-sync pytest` registrou 79 testes aprovados no Windows,
  incluindo dez do histórico. Os 16 testes de PostgreSQL ficaram para o CI.
- Os testes exercitam os formatos Spot e Futures, datas em UTC, precisão
  decimal, dados inválidos, integridade do ZIP e rejeição da configuração LIVE.
- As duas coletas públicas foram executadas com os comandos do
  [guia de coleta](../runbooks/historico-btcusdt.md).

A evidência de qualidade cobre um dia em cada mercado. Janelas maiores,
persistência operacional, ingestão contínua, ressincronização e recuperação
automática de lacunas permanecem no escopo de I01. G0 segue aberto.
