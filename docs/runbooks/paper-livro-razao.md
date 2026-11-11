# Livro razão de fills e saldos em PAPER

A revisão `0008` cria `trade_system.paper_account` e
`trade_system.paper_fill`. O livro razão aceita o runtime PAPER e
reutiliza Control e Risk do simulador Spot. Os dados e preços são
sintéticos.

Ao submeter uma intenção, o livro bloqueia a linha da conta, verifica
a chave de conta e intenção e grava o fill e os saldos na mesma
transação. Um reenvio idêntico dentro da validade devolve o fill
persistido. O mesmo ID com conteúdo diferente é recusado. A
reconciliação percorre os fills na ordem gravada, refaz caixa e posição
desde os saldos de abertura e compara com os saldos persistidos.
O relatório identifica o primeiro fill divergente e preserva os dados.

## Reproduzir no VS Code

Use um [PostgreSQL 17 descartável](postgresql-local.md) em `base`, com a
senha na sessão PowerShell. A suíte aplica e reverte as migrations.

```powershell
$env:TRADE_SYSTEM_ENVIRONMENT = "PAPER"
$env:LIVE_ENABLED = "false"
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest -v tests/integration -k paper_
Remove-Item Env:RUN_POSTGRES_TESTS
```

O teste de reinício usa dois processos Python separados conectados
ao mesmo banco. O teste de rollback força uma falha na atualização
da conta depois da inserção do fill. A reversão de `0008` remove as
tabelas e os dados simulados nelas gravados.

Este recorte mantém a simulação Spot com fill integral. Integração com
Market State, taxas, slippage e modelos adicionais seguem em I03.
LIVE permanece indisponível e G0 segue aberto.
