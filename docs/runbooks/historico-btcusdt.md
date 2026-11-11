# Histórico do BTCUSDT no VS Code

A primeira etapa de I01 coleta arquivos diários públicos de candles
fechados do BTCUSDT. Cada execução seleciona Spot ou USDⓈ-M Futures e
um intervalo de 1m, 5m, 15m ou 1h. Os mercados ficam em diretórios
distintos. A fonte publica checksums para os arquivos originais.
[Binance Public Data](https://github.com/binance/binance-public-data)

No terminal PowerShell, na raiz do checkout:

```powershell
uv sync --locked
$env:TRADE_SYSTEM_ENVIRONMENT = "TRAINING"
$env:LIVE_ENABLED = "false"
uv run --no-sync python -m apps.market_data --market spot --date 2025-11-10 --interval 5m
uv run --no-sync python -m apps.market_data --market futures-um --date 2025-11-10 --interval 5m
```

O comando imprime o caminho do manifesto. Abra a pasta correspondente
em `data/market-history/` no Explorador do VS Code:

- `source.zip` contém o arquivo original, verificado pelo SHA-256 da Binance.
- `candles.csv` contém uma linha por abertura de candle. As datas estão
  em UTC e o horário de fechamento é exclusivo. Os valores decimais mantêm
  a representação da fonte.
- `manifest.json` registra mercado, símbolo, data UTC, granularidade,
  URLs, timestamps de coleta e disponibilidade, contagem e hashes.

Cada execução válida cria um snapshot separado. Dias incompletos,
duplicatas, lacunas, timestamps incorretos e OHLCV inválido interrompem
a coleta antes da publicação do snapshot. `received_at` e
`available_at` identificam a ingestão do arquivo e não representam
quando um agente histórico teria recebido cada candle.

## Coletar uma janela e persistir no PostgreSQL

Inicie o [PostgreSQL local](postgresql-local.md), defina a senha do banco
na sessão e aplique as migrations. A janela usa dias UTC completos e
inclui as duas datas. Cada comando carrega um mercado.

```powershell
$env:TRADE_SYSTEM_ENVIRONMENT = "TRAINING"
$env:LIVE_ENABLED = "false"
uv run --no-sync alembic upgrade head
uv run --no-sync python -m apps.market_data --market spot --start 2025-11-04 --end 2025-11-10 --persist
uv run --no-sync python -m apps.market_data --market futures-um --start 2025-11-04 --end 2025-11-10 --persist
```

A revisão `0006` cria `trade_system.market_candle` e
`trade_system.market_history_source`. Uma chave estrangeira liga cada
candle ao manifesto diário. Preços e volumes usam `NUMERIC`, e os
horários usam `TIMESTAMPTZ`. O comando verifica os arquivos locais antes
de iniciar a transação. Uma carga idêntica preserva o manifesto original
e não cria candles duplicados. Se o arquivo de uma data já carregada
mudar, a transação inteira é revertida para revisão da origem.

Para inspecionar a janela:

```sql
SELECT market, count(*) AS candles, count(DISTINCT day_utc) AS dias
FROM trade_system.market_candle
WHERE symbol = 'BTCUSDT' AND interval = '5m'
  AND day_utc BETWEEN DATE '2025-11-04' AND DATE '2025-11-10'
GROUP BY market
ORDER BY market;
```

O [registro de evidências](../evidence/I01-persistencia-btcusdt.md) descreve
a carga de validação e o dump local. O comando usa HTTPS público e a
política local aceita TRAINING e PAPER. LIVE permanece indisponível.
Ingestão contínua e recuperação automática de lacunas seguem em I01.
