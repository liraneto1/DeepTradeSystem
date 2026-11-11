# Evidências de persistência histórica do BTCUSDT

Validação em 11/11/2026 com PostgreSQL 17.11 local e descartável. A carga
cobre sete dias UTC completos, de 04 a 10/11/2025, com candles fechados de
5 minutos. Os arquivos originais foram conferidos contra os SHA-256
publicados pela fonte. [Binance Public Data](https://github.com/binance/binance-public-data)

| Mercado | Candles esperados e gravados | Dias | Lacunas | Aberturas duplicadas | Candles sem origem |
|---|---:|---:|---:|---:|---:|
| Spot | 2.016 de 2.016 | 7 | 0 | 0 | 0 |
| USDⓈ-M Futures | 2.016 de 2.016 | 7 | 0 | 0 | 0 |

A consulta no PostgreSQL comparou a abertura de cada candle com o
fechamento exclusivo do anterior, inclusive na virada do dia. Verificou
as chaves únicas, a cobertura da janela e o vínculo com os 14 manifestos
em `trade_system.market_history_source`. Os dois mercados começam em
`2025-11-04T00:00:00Z` e terminam no fechamento exclusivo de
`2025-11-11T00:00:00Z`. A reimportação inseriu zero candles e reconheceu
sete dias idênticos em cada mercado.

## Testes

- A suíte local passou com **98 testes**, incluindo 19 de integração
  em PostgreSQL. Ruff, mypy e build passaram.
- Os testes novos verificam carga em ambos os mercados, precisão
  decimal, vínculo com a origem, reimportação, rejeição de lacuna e
  de arquivo alterado, e rollback da janela em caso de revisão de origem.
- A migration `0006` foi aplicada e revertida durante a suíte.

## Recuperação da amostra

O dump de dados `data/market-history/i01-btcusdt-2025-11-04_2025-11-10.pgcustom`
contém as duas tabelas. SHA-256
`a95de5d735c1fe3ae11252ec3dd8ab4a7b644af75c062c87b089648028a5a262`.
O dump foi restaurado em um segundo banco PostgreSQL 17 descartável
com a revisão `0006`, recuperando 4.032 candles e 14 manifestos.

Os ZIPs, CSVs, manifestos e o dump ficam no checkout local. O
[guia de coleta](../runbooks/historico-btcusdt.md) descreve como reproduzir
a carga. A evidência cobre esta janela. Ingestão contínua, ressincronização
e recuperação automática de lacunas permanecem em I01. LIVE segue
indisponível e G0 permanece aberto.
