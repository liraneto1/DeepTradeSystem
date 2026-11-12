# I03 — Preço de marcação e liquidação automática em PAPER

O processo consulta o preço público de marcação de BTCUSDT USDⓈ-M.
O horário da fonte identifica a observação e o recebimento local
define sua disponibilidade. O livro valida os dois horários, a
idade máxima e a ordem em relação a fills, funding e liquidações.
A revisão `0014` já contém a tabela de liquidações.

Em um reinício, a mesma marcação liquidada pode chegar em outro
horário local. Sob o bloqueio da conta, o livro compara o preço,
a origem e a política com a liquidação gravada. Mantém a primeira
disponibilidade e aplica zero novos lançamentos. Uma marcação com
preço diferente na mesma chave é tratada como conflito.

## Evidências

- `python -m ruff check src infrastructure apps tests` passou.
- `python -m ruff format --check src infrastructure apps tests` passou em 82 arquivos.
- `python -m mypy` passou em 82 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 141 testes.
- A integração PostgreSQL testa marcação futura, indisponível ou
  vencida. Após reabrir a conexão, repete a marcação com outro
  horário de recebimento e verifica uma única liquidação,
  disponibilidade original e saldo reconciliado de 940 USDT.
- A CLI com `--once` consultou a API pública e avaliou uma
  marcação em conta PAPER descartável sem posição. Registrou
  zero liquidações.

A coleta avalia amostras atuais, com intervalo de cinco segundos.
O [guia de execução](../runbooks/paper-futures.md) descreve o
comando e a limitação de cobertura durante interrupções.
O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
do commit `e8f7b51` seguia na fila na consulta desta entrega.
LIVE permanece indisponível e G0 segue aberto.
