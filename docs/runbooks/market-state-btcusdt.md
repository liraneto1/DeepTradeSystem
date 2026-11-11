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

## Consultar quatro intervalos

Carregue candles nativos de `1m`, `5m`, `15m` e `1h` para o mercado
escolhido. Use o [guia de carga](historico-btcusdt.md) e altere
`--interval` para cada granularidade. Depois execute:

```powershell
uv run --no-sync python -m apps.market_data.state --market spot --close-at 2025-11-10T22:35:00Z --multi-interval
```

A saída `2.0.0` usa o fechamento de 5m como referência. Cada contexto
termina no último fechamento do seu intervalo até esse instante.
Às 22:35 UTC, os cortes são 22:35 para 1m e 5m, 22:30 para 15m e
22:00 para 1h. As quatro janelas são lidas no mesmo snapshot do
PostgreSQL, com 21 candles consecutivos e uma referência de origem
por candle. Se uma janela falhar, o comando bloqueia o estado inteiro.

O formato de 5m `1.0.0` continua disponível pelo comando inicial.
O recorte é diagnóstico. LIVE permanece indisponível.
