# Outbox transacional no PostgreSQL

Uma alteração de estado e o evento que a descreve precisam ser gravados na
mesma transação. Com a Outbox, um commit confirma os dois registros. Se a
operação falhar antes do commit, o rollback desfaz os dois.

A revisão `0002` cria `trade_system.outbox`. A tabela guarda o
[EventEnvelope v1](../../contracts/jsonschema/event-envelope.v1.schema.json)
como JSONB, usa `event_id` como chave primária e registra `enqueued_at` com
fuso horário. O banco confere que o identificador do envelope coincide com
a chave gravada.

A função `append_event(connection, envelope)` recebe um envelope já
validado e a mesma conexão usada para alterar o estado. Abra a transação
com `engine.begin()`, faça a alteração de estado e chame `append_event`
antes de sair do bloco. Deixe os erros propagarem para que o contexto
faça rollback. A função apenas executa o INSERT.

## Reproduzir no VS Code

Suba um banco descartável conforme o [guia de PostgreSQL](postgresql-local.md).
Com a senha na sessão PowerShell e o banco em `base`, execute:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest tests/integration/test_postgres_migrations.py
Remove-Item Env:RUN_POSTGRES_TESTS
```

Os testes criam uma tabela de estado sintético apenas durante a execução.
Após um commit, uma nova conexão lê o estado e o envelope persistidos.
Após uma falha injetada antes do commit, ambos ficam ausentes. A suíte
também verifica a reversão da migration e a rejeição de um ID duplicado.

O downgrade de `0002` remove a tabela e os eventos nela armazenados.
O dispatcher e o acompanhamento de publicação serão tratados em I00-06.
