# Evidências de I00-09

Validação local em 11/11/2026 com Windows x64, Python 3.12.12 e uv 0.9.26.
A entrega segue TS-ADR-098 e cobre o isolamento e a indisponibilidade de LIVE
no escopo de I00-AC10.

| Verificação | Resultado local |
|---|---|
| `uv sync --locked` | Lockfile com 57 pacotes resolvidos. |
| `uv run --no-sync ruff check src infrastructure apps tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure apps tests` | 42 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 42 arquivos-fonte. |
| `uv run --no-sync pytest` | 67 testes passaram. Doze testes PostgreSQL foram pulados no Windows sem instância local. |
| `uv run --no-sync alembic upgrade 0004:head --sql` | Gerou as restrições para novos registros na Outbox e na fila. |
| `uv run --no-sync alembic downgrade head:0004 --sql` | Gerou a remoção das restrições. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

Os testes locais verificam o bloqueio de políticas ausentes, inválidas ou
LIVE, a validação de senha e porta e o mascaramento da senha na URL.
A API recusa a inicialização com política inválida. Com política válida e
banco indisponível, ela mantém a saúde da API e retorna `503` na prontidão.

Os testes de integração em PostgreSQL 17 verificam a seleção de eventos por
ambiente, a rejeição de gravações cruzadas pelos aplicativos e a rejeição de
eventos LIVE pelo próprio banco. A separação entre TRAINING e PAPER é lógica
na instância local compartilhada. A revisão `0005` preserva os dados existentes.

Veja o [guia de isolamento e segredos](../runbooks/isolamento-e-segredos.md)
para configurar o terminal do VS Code.
