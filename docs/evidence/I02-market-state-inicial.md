# Evidências iniciais de I02

Validação em 11/11/2026 com PostgreSQL 17.11 e o dump restaurado de I01.
A suíte passou com 106 testes. Ruff, formatação e mypy passaram.

Para o fechamento de 10/11/2025 às 00:30 UTC, o comando produziu um
Market State por mercado. Cada estado usou 21 candles consecutivos
e apontou para dois manifestos diários de origem.

| Mercado | Último fechamento | SMA de 20 candles |
|---|---:|---:|
| Spot | 105513.04000000 | 104880.40450000 |
| USDⓈ-M Futures | 105448.30 | 104829.84 |

Com `--as-of 2025-11-10T00:30:00Z`, a API de linha de comando recusou
os dois estados porque os arquivos da amostra só ficaram disponíveis
depois desse instante. A evidência cobre um fechamento de cinco
minutos em cada mercado. O contexto multi-intervalo e features
adicionais seguem em I02. LIVE permanece indisponível e G0 segue aberto.
[Guia de Market State](../runbooks/market-state-btcusdt.md)
