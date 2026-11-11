# Evidências de I00-05

Validação local em 11/11/2026 com Windows x64, Python 3.12.12 e uv 0.9.26.
A entrega segue TS-ADR-092 e TS-ADR-093. O critério I00-AC05 é a atomicidade
entre a gravação de estado e a inclusão do evento na Outbox.

| Verificação | Resultado local |
|---|---|
| `uv sync --locked` | 41 pacotes conferidos. |
| `uv run --no-sync ruff check src infrastructure tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure tests` | 23 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 23 arquivos-fonte. |
| `uv run --no-sync pytest` | 39 testes passaram. Quatro testes de PostgreSQL foram pulados no Windows sem instância local. |
| `uv run --no-sync alembic upgrade 0001:head --sql` | Gerou a tabela, a chave primária e a restrição de identidade do evento. |
| `uv run --no-sync alembic downgrade head:0001 --sql` | Gerou a remoção da tabela Outbox e o retorno à revisão `0001`. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

O GitHub Actions executa os quatro testes de integração em PostgreSQL 17.
Eles verificam a reversão das migrations, a visibilidade conjunta após o
commit, a ausência de ambos os registros após rollback e a reversão de
uma nova alteração de estado quando o banco rejeita um evento duplicado.

Veja o [guia da Outbox](../runbooks/outbox-transacional.md) para reproduzir
os testes no VS Code. O dispatcher é o próximo pacote, I00-06.
