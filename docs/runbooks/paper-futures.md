# Simulação USDⓈ-M Futures em PAPER

A revisão `0011` cria um livro-razão para BTCUSDT Futures com caixa em
USDT, posição assinada, preço de entrada, margem reservada e P&L
realizado. Control autoriza o pedido, Risk valida a cotação e os limites,
e o livro grava o fill e o saldo na mesma transação. O modelo usa uma
posição por conta, margem isolada simulada a 1× e fechamento integral
com `reduce_only`.

Na abertura, o caixa reserva o nocional do fill e paga a taxa. No
fechamento, o caixa recebe a margem devolvida e o P&L realizado, menos
a taxa de fechamento. O P&L bruto é a quantidade assinada da posição
vezes a diferença entre o preço de saída e o de entrada. A política de
taxas e slippage fica gravada por fill para reprodução.

A partir da revisão `0012`, use `submit_futures_market_intent` em
`apps/market_data/paper.py` para cotar a intenção pelo Market State de
USDⓈ-M Futures. Informe o fechamento de 5m em `close_at` e o instante
de execução em `now`. Depois da autorização por Control, a leitura
alinha 1m, 5m, 15m e 1h e usa `intent.issued_at` como limite de
disponibilidade dos candles. O fechamento de 5m fornece a cotação.
Risk verifica sua idade no instante da execução.

O fill guarda o estado, a linhagem e a referência SHA-256 na mesma
transação que atualiza o saldo. A reconciliação verifica a presença
e a integridade dessa evidência. Cotações sintéticas continuam
disponíveis pelo método `submit`.

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
Funding, liquidação e alavancagem superior a 1× seguem fora deste
recorte. A reversão de `0012` remove a evidência Market State dos fills.
A reversão de `0011` remove as tabelas do livro Futures. LIVE permanece indisponível
e G0 segue aberto.
