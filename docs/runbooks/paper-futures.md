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
Liquidação e alavancagem superior a 1× seguem fora deste recorte.
A reversão de `0012` remove a evidência Market State dos fills.
A reversão de `0011` remove as tabelas do livro Futures. LIVE permanece indisponível
e G0 segue aberto.


## Funding simulado

A revisão `0013` registra funding de BTCUSDT em USDⓈ-M Futures.
A simulação recebe horário do evento, horário em que os dados ficaram
disponíveis, taxa, preço de marcação e referência da observação. A taxa
é uma fração, de modo que
`Decimal("0.0001")` representa 0,01%. A documentação da corretora
descreve os campos de referência.
[Histórico de funding USDⓈ-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History)

Para simular uma observação manualmente com uma conta PAPER já aberta:

```python
from datetime import UTC, datetime
from decimal import Decimal

from trade_system.risk.futures import FundingObservation

event = FundingObservation(
    funding_at=datetime(2025, 11, 10, 16, 0, tzinfo=UTC),
    available_at=datetime(2025, 11, 10, 16, 0, 2, tzinfo=UTC),
    mark_price=Decimal("20000"),
    rate=Decimal("0.0001"),
    reference="fixture:btcusdt-funding",
)
settlement = ledger.apply_funding(event, as_of=event.available_at)
report = ledger.reconcile()
```

O ajuste em USDT é `-quantidade assinada × preço de marcação × taxa`.
Com taxa positiva, uma posição comprada paga e uma vendida recebe.
Uma conta sem posição recebe um lançamento de valor zero. Se o débito
exceder o caixa livre, a transação é rejeitada. Margem e P&L de fills
continuam registrados nos próprios campos.

Em um replay, aplique o funding após a observação ficar disponível e
antes de submeter fills no instante do evento ou posteriores. O livro
rejeita funding retroativo quando um desses fills já estiver gravado.
Reenviar a mesma observação para a conta e o mesmo horário devolve o
lançamento gravado. Mudar a observação nessa chave gera conflito.
A reconciliação reproduz funding e fills na ordem registrada. A
reversão de `0013` exige que a tabela de funding esteja vazia.


### Coleta automática

Com a revisão `0013` aplicada, uma conta Futures PAPER aberta e a
[configuração local PAPER](paper-livro-razao.md), execute no terminal
do VS Code. Substitua o ID e o horário pelos da sua simulação.

```powershell
uv run --no-sync python -m apps.market_data.funding --account paper-test --start 2026-11-10T16:00:00+00:00
```

O processo consulta o histórico público de funding de BTCUSDT a cada
60 segundos. Use `--once` para executar uma única coleta. O horário
inicial é inclusivo e exige fuso horário. Em cada execução, a coleta
começa após o último funding gravado para a conta, respeitando o
horário inicial. Respostas vazias mantêm o cursor. Um bloqueio no
PostgreSQL limita a execução a um coletor por conta.

O fim de cada janela é fixado antes da consulta. A disponibilidade
dos dados é registrada quando o processo recebe a resposta, inclusive
em consultas históricas. O coletor aplica as observações em ordem.
Falhas de rede, HTTP 429 e erros de servidor são tentados novamente no
modo contínuo. Cada lançamento confirmado sobrevive ao reinício.

Durante a recuperação, processe o funding antes de retomar os fills.
Se houver fill já registrado no instante do funding ou posterior,
o coletor encerra com erro de ordenação e a conta requer revisão.
A coleta usa somente o endpoint público de histórico.
