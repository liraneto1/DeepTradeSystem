# Evidências do Market State multi-intervalo

Validação em 11/11/2026 no PostgreSQL 17.11 descartável. Restaurei
o histórico de 5m de I01 e carreguei os candles nativos de 10/11/2025
nos demais intervalos. Por mercado, foram gravados 1.440 candles
de 1m, 96 de 15m e 24 de 1h, com manifestos e hashes da origem.

| Referência de decisão UTC | 1m | 5m | 15m | 1h |
|---|---|---|---|---|
| 10/11/2025 às 22:35 | 22:35 | 22:35 | 22:30 | 22:00 |

Spot e USDⓈ-M Futures produziram as quatro janelas alinhadas, com
21 candles e referências de disponibilidade, URL, ID de coleta e
SHA-256 por janela. Os dois estados foram recusados quando
`--as-of` foi definido para o próprio horário histórico da decisão,
anterior à coleta dos arquivos.

Ruff, formatação, mypy e 107 testes passaram. O novo teste cobre
alinhamento, integridade de todas as janelas, atraso de disponibilidade
em 1h e corte de decisão fora da grade de 5m.

O ensaio cobre um fechamento em cada mercado. A saída `2.0.0` mantém
a versão das features e acrescenta o agrupamento por intervalo.
LIVE permanece indisponível e G0 segue aberto.
[Guia do Market State](../runbooks/market-state-btcusdt.md)
