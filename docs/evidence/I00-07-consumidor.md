# Evidências de I00-07

Validação local em 11/11/2026 com Windows x64, Python 3.12.12 e uv 0.9.26.
O consumidor segue TS-ADR-090 e TS-ADR-093. O teste de replay verifica
I00-AC06 para o efeito de diagnóstico gravado no PostgreSQL.

| Verificação | Resultado local |
|---|---|
| `uv sync --locked` | 41 pacotes conferidos. |
| `uv run --no-sync ruff check src infrastructure apps tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure apps tests` | 34 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 34 arquivos-fonte. |
| `uv run --no-sync pytest` | 39 testes passaram. Nove testes PostgreSQL foram pulados no Windows sem instância local. |
| `uv run --no-sync python -m apps.event_consumer --help` | Exibiu a opção `--once`. |
| `uv run --no-sync alembic upgrade 0003:head --sql` | Gerou a confirmação na fila, o registro de deduplicação e o contador. |
| `uv run --no-sync alembic downgrade head:0003 --sql` | Gerou a reversão para a fila de I00-06. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

O CI executa a suíte de integração em PostgreSQL 17. O teste de replay
insere duas entregas com o mesmo `event_id` e chama o comando do consumidor
em dois processos separados. Ele exige duas confirmações, um registro de
deduplicação e contador igual a 1. O teste de falha injeta uma exceção
depois do incremento e verifica que o contador, a deduplicação e a
confirmação são revertidos. Na repetição, o evento produz o efeito uma vez.

Veja o [guia do consumidor](../runbooks/consumidor-idempotente.md) para
reproduzir a validação no VS Code.
