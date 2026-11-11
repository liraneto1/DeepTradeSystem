# Consumidor idempotente no VS Code

O dispatcher pode colocar duas entregas do mesmo evento na fila. Cada
entrega tem seu próprio `delivery_id`, mas ambas carregam o mesmo
`event_id`. O consumidor usa esse identificador para aplicar o efeito
uma única vez.

A revisão `0004` cria `trade_system.processed_event` e adiciona
`consumed_at` à fila. O consumidor bloqueia a entrega pendente mais antiga
durante o processamento. O registro de deduplicação, o incremento do
contador de diagnóstico e a confirmação da entrega usam a mesma
transação. Uma duplicata confirma apenas a própria entrega. Se o handler
falhar, a entrega fica pendente e a tentativa pode ser repetida.

O efeito de demonstração é um contador de eventos `diagnostics.synthetic.created`
por ambiente em `trade_system.diagnostic_event_count`. Ele aceita a versão
`1.0.0` em `TRAINING` e `PAPER`. Uma mensagem inédita fora desse recorte
interrompe o processo e permanece pendente para investigação.

## Executar no VS Code

Com o [PostgreSQL local](postgresql-local.md) iniciado e a senha disponível
na sessão PowerShell:

```powershell
uv run --no-sync alembic upgrade head
uv run --no-sync python -m apps.event_consumer --once
```

`--once` processa até uma entrega. Remova a opção para aguardar novas
entregas e use **Ctrl+C** para encerrar. Em um banco descartável no estado
`base`, reproduza o cenário de duplicação e o rollback:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest tests/integration
Remove-Item Env:RUN_POSTGRES_TESTS
```

A garantia de deduplicação vale para efeitos gravados pelo handler na
mesma transação PostgreSQL. A reversão de `0004` remove o histórico de
consumo e o contador. Ao reaplicar a revisão, as entregas existentes
voltam a ficar pendentes.
