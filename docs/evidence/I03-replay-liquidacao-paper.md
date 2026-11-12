# I03 — Replay de liquidação em PAPER

O replay usa os fechamentos de 1 minuto recuperados pela revisão
`0015`. A disponibilidade do candle é comparada com o corte da
consulta. A posição vem do histórico da conta no fechamento do
candle. A transação PostgreSQL é somente leitura, com isolamento
Repeatable Read. O resultado mostra o primeiro gatilho e o saldo
hipotético, se houver. Lacunas e extremos intraminuto ficam fora
da avaliação. [Guia de execução](../runbooks/paper-futures.md)

## Evidências

- Ruff e mypy passaram em 85 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 144 testes.
- A integração excluiu candles antes do recebimento, rejeitou uma
  janela posterior ao corte e reproduziu o mesmo resultado em dois
  replays. O saldo hipotético foi de 940 USDT. A reconciliação
  persistida permaneceu em 1.000 USDT com dois fills e zero liquidações.
- O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
  seguia na fila. LIVE permanece indisponível e G0 segue aberto.
