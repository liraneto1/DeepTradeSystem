# Consolidação de I01

A ingestão contínua foi aprovada pelo usuário em 11/11/2026. O recorte
é BTCUSDT na Binance Spot e USDⓈ-M Futures, com dados públicos.

| Entrega | Evidência |
|---|---|
| Coleta diária | 288 candles de 5 minutos por mercado em 10/11/2025. ZIPs verificados com o SHA-256 da fonte. [Coleta histórica](I01-historico-btcusdt.md) |
| Histórico persistido | 4.032 candles em sete dias UTC, sem lacunas, duplicatas ou candles órfãos. Reimportação inseriu zero linhas. Dump restaurado. [Persistência](I01-persistencia-btcusdt.md) |
| Ingestão contínua | Reconexão real em ambos os mercados. Cada coletor recuperou um candle via REST e retomou o WebSocket. [Ensaio de reconexão](I01-ingestao-continua-btcusdt.md) |

A [execução de CI de `e8f7b51`](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
estava na fila, sem job iniciado, na verificação de 11/11/2026. A
validação local em PostgreSQL 17 registrou 101 testes aprovados e mais
três testes de protocolo em uma execução separada. O CI da persistência
[passou no commit `69f05a3`](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43093300450).

A evidência cobre a janela histórica carregada e o ensaio curto de
reconexão. G0 segue aberto e LIVE permanece indisponível.
