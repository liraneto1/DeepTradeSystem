# 00 — Baseline e escopo

## Estado aprovado
- `TS-ARCH-GLOBAL-V1.0`: seis etapas aprovadas; G01–G60, 88 ADRs de domínio, 33 componentes lógicos, 106 pendências, F01–F10, 14 épicos, 24 histórias iniciais, I00–I09 e gates G0–G5.
- `TS-ENG-I00-V1.0`: T01–T10 aprovadas; TS-ADR-089–098 aprovadas. Monorepo modular e stack Python aprovados.
- A arquitetura está aprovada; implementação, PAPER Qualified e LIVE **não** estão homologados.

## Escopo I00
Monorepo, toolchain, CI, contratos versionados, PostgreSQL, migrations, Outbox, dispatcher, consumidor idempotente, API de diagnóstico local, segurança mínima, telemetria, testes e Evidence Bundle.

## Fora do escopo I00
Agente PPO treinado; dados de mercado Binance reais; execução de ordens Spot/Futures; UI operacional completa; promoção de modelos; deploy LIVE; capital real.

## Roadmap global (planejamento)
I00 fundação; I01 Market Data; I02 Features/Market State; I03 PAPER Trading Core; I04 PPO; I05 backtest e walk-forward; I06 PAPER E2E; I07 LIVE readiness; I08 LIVE limitado após autorização; I09 LIVE controlado após evidência e aprovação. Não inferir autorização de LIVE pelo roadmap.

## Domínios
D01 Market Data & Features (3 componentes, ADR001–006, P01–P08); D02 AI & Learning (3, ADR007–016, P09–P18); D03 Risk, Execution & Control (4, ADR017–028, P19–P32); D04 Operations UI (5, ADR029–040, P33–P47); D05 Data, Events & Audit (6, ADR041–054, P48–P64); D06 Infrastructure & Security (6, ADR055–070, P65–P84); D07 Engineering, QA & Validation (6, ADR071–088, P85–P106).

## Priorização provisória
M0=68; M1=28; M2=9; M3=1. A fase de P18 permanece provisória. Segurança mínima necessária para PAPER é antecipada para M0 mesmo quando uma pendência primária for M1.
