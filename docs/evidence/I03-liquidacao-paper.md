# I03 — Liquidação simulada de BTCUSDT em PAPER

A revisão `0014` registra a liquidação integral de uma posição isolada.
Risk calcula a margem disponível com o P&L ao preço de marcação e
compara com o nocional de marcação multiplicado pela taxa de manutenção
informada. No limite ou abaixo dele, a posição é encerrada. O caixa
recebe o saldo positivo da margem e a perda fica limitada ao colateral
reservado. A taxa de manutenção é um parâmetro da simulação.

O livro rejeita observações futuras, indisponíveis, vencidas ou
anteriores ao último lançamento relevante. A liquidação e o saldo são
persistidos na mesma transação. A reconciliação reproduz fills, funding
e liquidações na ordem do livro, usando a política persistida.
[Guia PAPER Futures](../runbooks/paper-futures.md)

## Evidências

- `python -m ruff check src infrastructure apps tests` passou.
- `python -m ruff format --check src infrastructure apps tests` passou em 79 arquivos.
- `python -m mypy` passou em 79 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 139 testes.
- A integração PostgreSQL verifica manutenção acima do limite,
  liquidação no limite, perda limitada à margem, corte de disponibilidade
  e validade, lançamentos retroativos, reenvio e reconciliação com funding.
  Uma alteração no valor de manutenção persistido sinaliza divergência.
- O teste de migrações verifica a reversão da tabela vazia.

O modelo mantém margem isolada a 1×, manutenção fixa e fechamento
integral. O preço de marcação é informado pelo chamador.
O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
do commit `e8f7b51` seguia na fila na consulta desta entrega.
LIVE permanece indisponível e G0 segue aberto.
