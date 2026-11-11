# Evidências da ingestão contínua do BTCUSDT

Validação em 11/11/2026 com PostgreSQL 17.11 descartável em loopback.
A migration `0007` registra a primeira observação de cada candle em
`trade_system.market_candle_observation`, com origem WebSocket ou REST,
URL, horários de ingestão e payload público. O mesmo candle pode ter
manifesto histórico verificado e observação contínua.

## Verificações automatizadas

- A suíte local com PostgreSQL passou com 101 testes, incluindo 22 de
  integração. Três testes adicionais do protocolo passaram em uma
  execução separada.
- Nos dois mercados, o teste simula desconexão, resposta REST
  incompleta, repetição de uma entrega e reinício com o ponto salvo.
  O PostgreSQL registra sete candles consecutivos em cada cenário.
- Outro teste confirma que a carga diária completa um dia já observado
  pelo WebSocket e mantém a primeira observação. A reimportação mantém
  as contagens.
- Ruff, formatação, mypy, lockfile e build passaram. O comando recusou
  a configuração LIVE antes de abrir o PostgreSQL ou o WebSocket.

## Ensaio com a fonte pública

Usei candles de um minuto para exercitar a virada de janela no ensaio.
Cada mercado teve duas conexões WebSocket e recuperou um candle via
REST depois da interrupção. A sequência gravada no PostgreSQL ficou
contínua, com uma linha por abertura e retomada pelo WebSocket.

| Mercado | Primeira e última abertura UTC | Candles | Recuperados via REST após a interrupção |
|---|---|---:|---:|
| Spot | 20:15 a 20:19 | 5 | 1 |
| USDⓈ-M Futures | 20:15 a 20:18 | 4 | 1 |

A interrupção foi provocada pelo roteiro de validação. O transporte
WebSocket e as consultas REST foram reais. Os bancos de teste foram
descartáveis. G0 permanece aberto.
[Guia de ingestão contínua](../runbooks/ingestao-continua-btcusdt.md)
