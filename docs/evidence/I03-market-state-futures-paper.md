# I03 — Market State de USDⓈ-M Futures em PAPER

A função `submit_futures_market_intent` liga TradingIntent → Control → Risk →
Execution para BTCUSDT em USDⓈ-M Futures. Control autoriza antes da consulta.
O Market State usa o fechamento de 5m como preço de referência e alinha os
intervalos de 1m, 5m, 15m e 1h. O corte de disponibilidade é o instante de
emissão da intenção. Risk valida a idade da cotação no instante da execução.

A migração `0012` permite gravar o estado e a linhagem em JSONB junto ao fill.
O saldo e o fill são persistidos na mesma transação. A reconciliação confere
a referência SHA-256 e reproduz os saldos. O guia está em
[Simulação USDⓈ-M Futures em PAPER](../runbooks/paper-futures.md).

## Evidência local

- `python -m ruff check src infrastructure apps tests` passou.
- `python -m ruff format --check src infrastructure apps tests` passou em 74 arquivos.
- `python -m mypy` passou em 74 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 133 testes.
- O teste `test_futures_market_state_cutoff_and_reconciliation` rejeitou
  o candle recebido após a emissão, o fechamento futuro e a cotação vencida.
  Verificou abertura e encerramento de posição vendida, 84 referências de
  candles por fill, reenvio após recriar o ledger, rejeição de LIVE e
  detecção de evidência removida.
- O teste `test_migrations_round_trip` validou a reversão de `0012`.

O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
do commit `e8f7b51` seguia na fila na consulta de 11/11/2026.
LIVE permanece indisponível e G0 segue aberto.
