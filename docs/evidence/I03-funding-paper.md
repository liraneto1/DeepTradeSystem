# I03 — Funding simulado de BTCUSDT em PAPER

A migração `0013` persiste a observação, o ajuste em USDT e o saldo
resultante. Funding e fills compartilham a sequência do livro Futures.
O lançamento e a atualização do saldo ocorrem na mesma transação, com
bloqueio da conta. O [guia PAPER Futures](../runbooks/paper-futures.md)
mostra como submeter uma observação e reconciliar o saldo.

A observação só pode ser lançada quando o instante do evento e o de
disponibilidade estiverem dentro do corte. A posição é a que existia
imediatamente antes do funding. Se houver fill gravado no instante do
evento ou posterior, o lançamento retroativo é rejeitado. A identidade
é conta e horário de funding. O reenvio idêntico devolve o lançamento
gravado. Uma observação alterada na mesma chave gera conflito.

## Evidências

- `python -m ruff check src infrastructure apps tests` passou.
- `python -m ruff format --check src infrastructure apps tests` passou em 75 arquivos.
- `python -m mypy` passou em 75 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 135 testes.
- A integração PostgreSQL verificou débito de 0,02 USDT em posição
  comprada e crédito de 0,02 USDT em posição vendida, corte temporal,
  rejeição de lançamento retroativo, reenvio após recriar o livro,
  conflito, lançamento zero sem posição e detecção de valor adulterado.
- O teste de migrações confirmou a reversão da tabela vazia.

A taxa e o preço de marcação são dados da simulação fornecidos pelo
chamador. Coleta e agendamento automáticos seguem fora deste recorte.
O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
do commit `e8f7b51` seguia na fila na consulta desta entrega. LIVE permanece
indisponível e G0 segue aberto.
