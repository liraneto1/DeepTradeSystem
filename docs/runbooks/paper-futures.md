# Simulação USDⓈ-M Futures em PAPER

A revisão `0011` cria um livro-razão para BTCUSDT Futures com caixa em
USDT, posição assinada, preço de entrada, margem reservada e P&L
realizado. Control autoriza o pedido, Risk valida a cotação e os limites,
e o livro grava o fill e o saldo na mesma transação. O modelo usa uma
posição por conta, margem isolada simulada a 1× e fechamento integral
com `reduce_only`. As cotações são sintéticas.

Na abertura, o caixa reserva o nocional do fill e paga a taxa. No
fechamento, o caixa recebe a margem devolvida e o P&L realizado, menos
a taxa de fechamento. O P&L bruto é a quantidade assinada da posição
vezes a diferença entre o preço de saída e o de entrada. A política de
taxas e slippage fica gravada por fill para reprodução.

Um reenvio idêntico dentro da validade devolve o fill gravado. A
reconciliação reexecuta a sequência de fills e compara caixa, posição,
margem e P&L com o saldo persistido.

Em um PostgreSQL 17 descartável em `base`, siga a
[configuração PAPER](paper-livro-razao.md) e execute:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest -v tests/integration -k futures
Remove-Item Env:RUN_POSTGRES_TESTS
```

A simulação atual exige fechamento integral e colateral suficiente.
Se a perda exceder a margem reservada, o modelo bloqueia o fill para
revisão.
Funding, liquidação, alavancagem superior a 1× e precificação pelo
Market State de Futures seguem fora deste recorte. A reversão de
`0011` remove as tabelas do livro Futures. LIVE permanece indisponível
e G0 segue aberto.
