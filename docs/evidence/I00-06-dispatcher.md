# Evidências de I00-06

Validação local em 11/11/2026 com Windows x64, Python 3.12.12 e uv 0.9.26.
A entrega segue TS-ADR-090 e TS-ADR-093. Os testes cobrem ordenação entre
eventos já enfileirados do mesmo agregado, recuperação da publicação e
logs de tentativas. São evidências de I00-AC07, I00-AC08 e I00-AC09 no
escopo do dispatcher.

| Verificação | Resultado local |
|---|---|
| `uv sync --locked` | 41 pacotes resolvidos. |
| `uv run --no-sync ruff check src infrastructure apps tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure apps tests` | 27 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 27 arquivos-fonte. |
| `uv run --no-sync pytest` | 39 testes passaram. Sete testes de PostgreSQL foram pulados no Windows sem instância local. |
| `uv run --no-sync python -m apps.event_dispatcher --help` | O comando carregou e exibiu a opção `--once`. |
| `uv run --no-sync alembic upgrade 0002:head --sql` | Gerou os campos de controle, o índice de pendências e a fila local. |
| `uv run --no-sync alembic downgrade head:0002 --sql` | Gerou a reversão para a Outbox de I00-05. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

No CI, a suíte PostgreSQL 17 verifica as migrations, a atomicidade da
Outbox e três cenários do dispatcher. Um worker concorrente pula a linha
bloqueada e preserva a ordem do agregado. Falhas de publicação agendam
retries até o limite. Uma interrupção após a confirmação na fila local
permite nova entrega do mesmo evento. Os logs registram os identificadores
de rastreio e omitem o conteúdo da mensagem e o texto da exceção.

Veja o [guia do dispatcher](../runbooks/dispatcher-outbox.md) para reproduzir
o processo no VS Code. I00-07 trata do consumo e da deduplicação persistente.
