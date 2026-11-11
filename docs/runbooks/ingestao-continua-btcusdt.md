# Ingestão contínua de BTCUSDT

Inicie o [PostgreSQL local](postgresql-local.md) e mantenha a senha
na sessão do PowerShell. Aplique a migration `0007` na raiz do checkout:

```powershell
$env:TRADE_SYSTEM_ENVIRONMENT = "TRAINING"
$env:LIVE_ENABLED = "false"
uv sync --locked
uv run --no-sync alembic upgrade head
```

Abra um terminal por mercado, com a mesma política local e a senha
disponível em cada sessão:

```powershell
uv run --no-sync python -m apps.market_data.continuous --market spot --interval 5m
uv run --no-sync python -m apps.market_data.continuous --market futures-um --interval 5m
```

Cada comando é contínuo. Use **Ctrl+C** para parar. A opção `--once`
encerra após receber um candle fechado pelo WebSocket. O primeiro início
busca o último candle fechado via REST e começa a acompanhar o mercado.
Nos reinícios, o coletor retoma após a última observação no banco. O
histórico anterior pode ser carregado pelo [coletor de arquivos](historico-btcusdt.md).

## Como a recuperação funciona

- O WebSocket só grava candles marcados como fechados. Ao conectar, o
  coletor busca via REST os candles fechados entre o ponto de retomada
  e o início da janela corrente. A chegada de um candle posterior também
  aciona a verificação do intervalo anterior.
- Cada página REST precisa cobrir todas as aberturas esperadas. Uma
  página incompleta provoca nova tentativa, sem avançar sobre a lacuna.
  A reconexão usa espera crescente e respeita `Retry-After` quando
  a fonte o envia. Respostas de acesso bloqueado encerram a coleta.
- A chave do candle continua sendo mercado, símbolo, intervalo e abertura.
  Uma entrega idêntica preserva o candle e a primeira observação. Valores
  conflitantes interrompem a carga para revisão. Um arquivo diário
  verificado pode complementar a origem de um dia já observado.
- A migration registra a origem WebSocket ou REST, a URL, os horários de
  ingestão e o payload público em `trade_system.market_candle_observation`.
  O candle e a observação são confirmados na mesma transação.

Para inspecionar a origem dos candles mais recentes:

```sql
SELECT market, interval, open_time_utc, source_kind, received_at, available_at
FROM trade_system.market_candle_observation
WHERE symbol = 'BTCUSDT'
ORDER BY open_time_utc DESC
LIMIT 20;
```

O downgrade para `0006` remove as observações e os candles dos dias que
possuem apenas origem contínua. Os candles vinculados a um arquivo diário
verificado permanecem.

A integração usa endpoints públicos de mercado. LIVE permanece
indisponível.
[WebSocket Spot](https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams)
· [WebSocket USDⓈ-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Connect)
