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

O comando usa HTTPS público e a política local aceita TRAINING e PAPER.
LIVE permanece indisponível. Persistência operacional, ingestão contínua
e recuperação automática de lacunas seguem como etapas de I01.
