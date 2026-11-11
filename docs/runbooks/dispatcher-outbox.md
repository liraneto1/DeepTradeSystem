# Dispatcher da Outbox no VS Code

O dispatcher lê eventos confirmados na Outbox e grava uma cópia em
`trade_system.event_delivery`, uma fila durável no PostgreSQL local. A revisão
`0003` adiciona essa fila e os campos de controle de tentativas à Outbox.

Com o [banco local](postgresql-local.md) iniciado e a senha na sessão PowerShell:

```powershell
uv run --no-sync alembic upgrade head
uv run --no-sync python -m apps.event_dispatcher --once
```

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
  já enfileiradas para o mesmo ambiente, conta e agregado.
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
