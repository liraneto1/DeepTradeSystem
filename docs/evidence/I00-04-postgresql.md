# Evidências de I00-04

Validação em 11/11/2026 no Windows x64, com Python 3.12.12 e uv 0.9.26.
A entrega segue TS-ADR-092 e TS-ADR-095. A revisão `0001` cria o schema
`trade_system` e reverte com `DROP SCHEMA` sem `CASCADE`.

| Verificação | Resultado local |
|---|---|
| `uv sync --locked` | 41 pacotes conferidos, incluindo SQLAlchemy 2.1.8, Alembic 1.20.1 e psycopg 3.3.8. |
| `uv run --no-sync ruff check src infrastructure tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure tests` | 20 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 20 arquivos-fonte. |
| `uv run --no-sync pytest` | 39 testes passaram. O teste de PostgreSQL foi pulado porque a instância local não estava disponível. |
| `uv run --no-sync alembic upgrade head --sql` | Gerou `CREATE SCHEMA trade_system` e o registro da revisão. |
| `uv run --no-sync alembic downgrade head:base --sql` | Gerou `DROP SCHEMA trade_system` e a remoção do registro da revisão. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

O OneDrive bloqueou a atualização da `.venv`. A verificação local foi
concluída com `UV_LINK_MODE=copy` e `UV_PROJECT_ENVIRONMENT` fora do OneDrive.
O [guia de PostgreSQL no VS Code](../runbooks/postgresql-local.md) descreve
como reproduzir o processo.

O teste de integração habilitado no GitHub Actions usa PostgreSQL 17 em um
Compose descartável. Ele confere a versão do servidor, a presença do schema
e da revisão após `upgrade head` e a reversão de ambos após `downgrade base`.
O resultado do job é a evidência de execução em banco para I00-AC04.
