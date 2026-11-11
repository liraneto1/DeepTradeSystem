# 02 — Backlog refinado I00

| Work package | Entrega | Dependências | Evidência |
|---|---|---|---|
| I00-01 | Bootstrap monorepo modular | — | Instalação e imports |
| I00-02 | Toolchain e lockfile | 01 | Lint, mypy, pytest |
| I00-03 | Command/Event schemas v1 | 01 | Contract tests |
| I00-04 | PostgreSQL e migrations | 01 | Migration upgrade/downgrade testado |
| I00-05 | Transactional Outbox | 03,04 | Rollback atômico |
| I00-06 | Dispatcher | 05 | Retry e observabilidade |
| I00-07 | Consumer idempotente | 06 | Replay sem efeito duplicado |
| I00-08 | API fundação | 02,03 | Health/readiness/info |
| I00-09 | Isolamento e segredos | 01 | Verificações fail-closed |
| I00-10 | Telemetria | 03,08 | Logs e correlation IDs |
| I00-11 | CI/CD e qualidade | 02 | Workflow verde |
| I00-12 | Registro mestre e rastreabilidade | 01 | Matriz com lacunas explícitas |
| I00-13 | Testes de falha | 05,07 | Falha/restart/retry |
| I00-14 | Evidence Bundle | 01–13 | Manifesto e evidências reais |

## Ordem de implementação sugerida
1. **Primeira PR:** I00-01, I00-02, I00-11 (somente bootstrap, sem domínio operacional).
2. **Segunda PR:** I00-03 e I00-04.
3. **Terceira PR:** I00-05 a I00-07.
4. **Quarta PR:** I00-08 a I00-10, I00-12 a I00-14.

Não presumir prazo ou capacidade de equipe. Cada PR deve declarar critérios atendidos e pendências.
