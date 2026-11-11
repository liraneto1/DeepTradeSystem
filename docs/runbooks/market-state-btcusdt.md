# Market State de BTCUSDT no VS Code

O primeiro recorte de I02 produz um estado JSON versionado para um
mercado e um fechamento de cinco minutos. Ele lê 21 candles consecutivos
do [histórico no PostgreSQL](historico-btcusdt.md), em ordem de abertura.

Com o banco local iniciado, migrations aplicadas e política TRAINING ou
PAPER válida, execute na raiz do checkout:

```powershell
uv run --no-sync python -m apps.market_data.state --market spot --close-at 2025-11-10T00:30:00Z
```

- `return_1` é a variação fracionária entre os dois últimos fechamentos.
- `sma_20` é a média dos últimos 20 fechamentos.
- `atr_sma_14` é a média aritmética dos últimos 14 true ranges.
- `relative_volume_20` compara o último volume com a média dos 20
  anteriores. Retorna `null` quando essa média é zero.

Os cálculos usam decimais e os valores são serializados como strings.
A saída inclui origem e disponibilidade de cada candle. `--close-at`
limita o tempo do evento e `--as-of` limita o tempo de disponibilidade.
O padrão de `--as-of` é o instante da consulta. Um arquivo histórico
carregado depois do evento fica indisponível em uma simulação cujo
`--as-of` anteceda a coleta. Lacunas e janelas incompletas bloqueiam o estado.

O recorte é diagnóstico. Contexto de outros intervalos e features
adicionais seguem em I02. LIVE permanece indisponível.
