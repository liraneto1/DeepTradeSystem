# 01 — Arquitetura física aprovada para I00

## Princípios
Monorepo Python, monólito modular, processos isoláveis para `api`, `event_dispatcher`, `event_consumer`. PostgreSQL é fonte autoritativa para estado transacional. Outbox transacional e consumidores idempotentes; entrega ao menos uma vez. Não exigir event sourcing integral. Fronteiras de domínio com interfaces explícitas.

## Stack aprovada
Python 3.12+; FastAPI/Pydantic v2; PostgreSQL 17; SQLAlchemy 2/Alembic; uv/pyproject; Ruff/mypy/pytest/Hypothesis; Docker Compose; GitHub Actions; OpenTelemetry/logs JSON; JSON Schema/OpenAPI. Fixar versões exatas no lockfile após verificar compatibilidade.

## Árvore-alvo
```text
DeepTradeSystem/
  AGENTS.md
  apps/{api,event_dispatcher,event_consumer}/
  src/trade_system/{shared,market_data,features,market_state,ai,control,risk,execution,portfolio,audit,operations}/
  infrastructure/{database,events,security,adapters}/
  contracts/{jsonschema,openapi,examples}/
  tests/{unit,contracts,integration,property,e2e,resilience}/
  deploy/{compose,docker,iac}/
  docs/{architecture,adr,domains,backlog,evidence,runbooks}/
  .github/workflows/
  pyproject.toml
  uv.lock
  .env.example
  README.md
```

## Regras de acoplamento
`shared` não contém regras de trading; domínios não escrevem tabelas de outros domínios; application services dependem de portas/interfaces; adapters implementam portas; sem imports circulares; API não concede autorização financeira; agente não fala com corretora.

## Fluxos globais
F01 market data/state; F02 AI decision; F03 control/risk; F04 execution; F05 fills/reconciliation; F06 emergency; F07 training/promotion; F08 manual trading; F09 audit/read models; F10 incident recovery.
