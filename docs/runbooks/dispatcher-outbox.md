# Dispatcher da Outbox no VS Code

O dispatcher lê eventos confirmados na Outbox e grava uma cópia em
`trade_system.event_delivery`, uma fila durável no PostgreSQL local. A revisão
`0003` adiciona essa fila e os campos de controle de tentativas à Outbox.

Com o [banco local](postgresql-local.md) iniciado, execute
`uv run --no-sync alembic upgrade head` usando a identidade de migração.
A revisão `0021` cria o papel de grupo `outbox_dispatcher_worker`.
No PostgreSQL, atribua esse papel a um login dedicado, sem privilégios
administrativos, usando a sessão de administração. No exemplo,
`outbox_dispatcher_login` é um login previamente provisionado.

```sql
GRANT outbox_dispatcher_worker TO outbox_dispatcher_login;
```

Na sessão PowerShell de PAPER ou TRAINING, configure
`OUTBOX_DISPATCHER_DB_USER` e injete `OUTBOX_DISPATCHER_DB_PASSWORD`
a partir do armazenamento local de segredos. Use o mesmo
`POSTGRES_PORT` do banco local e mantenha `LIVE_ENABLED=false`.

```powershell
$env:OUTBOX_DISPATCHER_DB_USER = "outbox_dispatcher_login"
uv run --no-sync python -m apps.event_dispatcher --once
```

A CLI exige as credenciais dedicadas. Na inicialização, verifica o
papel do login, os atributos administrativos e os privilégios de
retenção e liberação. O papel de dispatcher permite publicação e
registro de tentativas e incidentes, sem conceder remoção ou
liberação das quarentenas.

`--once` tenta publicar até um evento disponível. Remova a opção para o
processo ficar aguardando eventos. Use **Ctrl+C** para encerrá-lo. Um banco
novo começa sem eventos. Os testes de integração geram eventos sintéticos
para demonstrar a publicação e as falhas.

## Tentativas e ordenação

- Após quatro falhas, os intervalos antes da próxima tentativa são 1, 2, 4
  e 8 segundos. Na quinta falha registrada, o evento fica retido com
  `failed_at` preenchido para investigação. Esses valores são padrões de
  desenvolvimento.
- O dispatcher bloqueia a linha enquanto publica. Outro processo pula a
  linha bloqueada e pode trabalhar em um agregado diferente. Um predecessor
  ainda pendente, inclusive um evento retido, bloqueia versões posteriores
  já enfileiradas para o mesmo ambiente, conta e agregado. Uma versão maior
  que 1 só é elegível após a publicação da versão imediatamente anterior.
  O dispatcher mantém outros agregados elegíveis enquanto espera.
- A fila confirma a publicação em uma transação própria. Se o processo
  parar entre essa confirmação e a atualização da Outbox, a próxima
  execução pode gravar outra entrega do mesmo `event_id`. A deduplicação
  persistente é feita pelo [consumidor idempotente](consumidor-idempotente.md).
- Os logs JSON registram resultado, ambiente, identificadores de
  correlação e causalidade, número da tentativa e atraso agendado. Em caso
  de falha, registram a classe do erro. O conteúdo do evento fica no banco.

Em um banco descartável no estado `base`, rode a suíte com
`$env:RUN_POSTGRES_TESTS = "1"` e `uv run --no-sync pytest tests/integration`.
Ao terminar, limpe a variável com `Remove-Item Env:RUN_POSTGRES_TESTS`.
