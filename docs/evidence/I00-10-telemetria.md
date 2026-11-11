# Evidências de I00-10

Validação local em 11/11/2026 com Windows x64, Python 3.12.12 e uv 0.9.26.
A entrega segue TS-ADR-096 e fornece evidências de I00-AC09 para logs
estruturados e correlação em três processos. OpenTelemetry 1.45.2
gera os spans locais. A entrega usa o JSON dos logs para consulta e
mantém a exportação externa desativada.

| Verificação | Resultado local |
|---|---|
| `uv sync --locked` | Lockfile com 59 pacotes resolvidos. |
| `uv run --no-sync ruff check src infrastructure apps tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure apps tests` | 44 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 44 arquivos-fonte. |
| `uv run --no-sync pytest` | 69 testes passaram. Treze testes PostgreSQL foram pulados no Windows sem instância local. |
| `python -m apps.api` e requisição HTTP a `/health` | Retornou 200, preservou `X-Correlation-ID` e registrou um objeto JSON sem a query nem o valor secreto sintético. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

Os testes da API cobrem IDs recebidos e gerados, mascaramento do segredo
sintético e falha interna sem texto de exceção. O teste PostgreSQL do CI
combina uma requisição de diagnóstico com um evento sintético que carrega
o mesmo ID. Ele compara os três registros, verifica IDs de evento e causa
nos workers e confirma que o payload fica fora dos logs.

Veja o [guia de telemetria](../runbooks/telemetria-local.md) para repetir
a consulta no VS Code.
