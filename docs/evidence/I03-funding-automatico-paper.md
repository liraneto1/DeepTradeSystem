# I03 — Coleta e aplicação automática de funding em PAPER

O coletor consulta o histórico público de BTCUSDT USDⓈ-M, pagina em ordem
ascendente e registra o recebimento como disponibilidade. O fim da janela
é fixado antes da consulta. O livro-razão aplica cada evento em uma
transação e mantém o cursor no último horário efetivamente gravado por
conta. O processo usa a migração `0013` existente.

A execução contínua consulta a cada 60 segundos e retoma falhas
transitórias de rede ou HTTP. O PostgreSQL admite um coletor por conta.
Se a conta tiver fill conflitante, a liquidação retroativa é bloqueada
para revisão. O [runbook PAPER Futures](../runbooks/paper-futures.md)
mostra a configuração, a execução contínua e a opção `--once`.

## Evidências

- `python -m ruff check src infrastructure apps tests` passou.
- `python -m ruff format --check src infrastructure apps tests` passou em 78 arquivos.
- `python -m mypy` passou em 78 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 137 testes.
- O teste de integração bloqueou eventos fora da janela e indisponíveis
  no corte. Interrompeu a coleta após a primeira gravação, recriou a
  conexão, aplicou o evento restante e confirmou zero duplicatas e
  saldo reconciliado de 899,96 USDT.
- A CLI consultou a API pública com uma conta descartável sem posição.
  Em dois processos com a mesma janela inicial, foram registrados três
  eventos na primeira execução e zero na segunda.

O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
do commit `e8f7b51` seguia na fila na consulta desta entrega. LIVE permanece
indisponível e G0 segue aberto.
