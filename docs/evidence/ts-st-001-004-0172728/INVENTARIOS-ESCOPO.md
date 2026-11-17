# Inventários de fronteiras, contratos, produtores e consumidores

Data 17/11/2026. Fonte exclusiva: árvore Git do candidato 0172728bd36c23247987a28c0fdccd32488e06f3. Inventário com as quatro decisões de escopo APPROVED pelo usuário em 17/11/2026.

## Fronteiras físicas

| Área | Diretórios versionados no candidato |
|---|---|
| apps | api, event_consumer, event_dispatcher, market_data |
| src/trade_system | ai, audit, control, execution, features, market_data, market_state, operations, portfolio, risk, shared |
| infrastructure | adapters, database, events, security |
| tests | contracts, e2e, integration, property, resilience, unit |
| contracts | examples, jsonschema, openapi |

### Comparação com I00-FEAT-001

A árvore proposta na seção 4 da Feature usa packages/d01_market_data etc. e apps/foundation_api. O candidato usa src/trade_system e apps/api. A própria Feature marca a árvore como PROPOSED e permite refinamento físico. Recomenda-se aprovar explicitamente o mapeamento físico e documentá-lo antes de encerrar ST001-AC01.

### Importações entre módulos de domínio

| Origem | Linha | Módulo importado |
|---|---|
| src/trade_system/execution/paper.py | 8 | trade_system.control.paper |
| src/trade_system/execution/paper.py | 9 | trade_system.risk.paper |
| src/trade_system/market_data/binance_funding.py | 13 | trade_system.risk.futures |
| src/trade_system/market_data/binance_mark.py | 14 | trade_system.risk.futures |
| src/trade_system/market_state/snapshot.py | 6 | trade_system.features.candles |
| src/trade_system/market_state/snapshot.py | 12 | trade_system.market_data.klines |
| src/trade_system/risk/execution_costs.py | 6 | trade_system.control.paper |
| src/trade_system/risk/futures.py | 7 | trade_system.control.paper |
| src/trade_system/risk/paper.py | 7 | trade_system.control.paper |

A inspeção AST cobre importações explícitas. Importações dinâmicas e dependências de execução requerem verificação própria.

## Contratos versionados

| Arquivo | Identidade | Versão | Propriedades adicionais |
|---|---|
| contracts/jsonschema/command-envelope.v1.schema.json | urn:deep-trade-system:contracts:command-envelope:1.0.0 | {'const': '1.0.0'} | raiz: False; payload: {'type': 'object'} |
| contracts/jsonschema/event-envelope.v1.schema.json | urn:deep-trade-system:contracts:event-envelope:1.0.0 | {'const': '1.0.0'} | raiz: False; payload: {'type': 'object'} |

Exemplos versionados: contracts/examples/command-envelope.example.json, contracts/examples/event-envelope.example.json.

### Modelos Pydantic auxiliares

| Arquivo | Linha | Modelo |
|---|---|
| apps/api/main.py | 28 | HealthResponse |
| apps/api/main.py | 33 | ReadinessChecks |
| apps/api/main.py | 38 | ReadinessResponse |
| apps/api/main.py | 44 | SystemInfoResponse |

Os modelos auxiliares têm escopo próprio. Recomenda-se aceitar TS-ST-002 pelo recorte de envelopes e manter contratos de conteúdo, catálogo completo e schema registry como cobertura remanescente de P61/P90.

## Produtores e consumidores — pontos de chamada

| Arquivo | Linha | Chamada |
|---|---|
| apps/event_consumer/__main__.py | 27 | consume_once |
| apps/event_consumer/__main__.py | 31 | consume_once |
| apps/event_dispatcher/__main__.py | 39 | LocalPublisher |
| apps/event_dispatcher/__main__.py | 68 | dispatch_once |
| apps/event_dispatcher/__main__.py | 72 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 387 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 397 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 409 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 410 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 469 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 489 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 523 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 548 | consume_once |
| tests/integration/test_postgres_migrations.py | 595 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 611 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 613 | consume_once |
| tests/integration/test_postgres_migrations.py | 626 | consume_once |
| tests/integration/test_postgres_migrations.py | 692 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 697 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 712 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 713 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 730 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 731 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 746 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2294 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2332 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2333 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2363 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2366 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2435 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2439 | consume_once |
| tests/integration/test_postgres_migrations.py | 2463 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2590 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2594 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2607 | consume_once |
| tests/integration/test_postgres_migrations.py | 2627 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2649 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2650 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2651 | consume_once |
| tests/integration/test_postgres_migrations.py | 2774 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2828 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2832 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2833 | consume_once |
| tests/integration/test_postgres_migrations.py | 283 | append_event |
| tests/integration/test_postgres_migrations.py | 309 | append_event |
| tests/integration/test_postgres_migrations.py | 323 | append_event |
| tests/integration/test_postgres_migrations.py | 327 | append_event |
| tests/integration/test_postgres_migrations.py | 378 | append_event |
| tests/integration/test_postgres_migrations.py | 399 | append_event |
| tests/integration/test_postgres_migrations.py | 400 | append_event |
| tests/integration/test_postgres_migrations.py | 401 | append_event |
| tests/integration/test_postgres_migrations.py | 405 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 411 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 422 | append_event |
| tests/integration/test_postgres_migrations.py | 423 | append_event |
| tests/integration/test_postgres_migrations.py | 431 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 468 | append_event |
| tests/integration/test_postgres_migrations.py | 476 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 479 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 481 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 504 | consume_once |
| tests/integration/test_postgres_migrations.py | 533 | consume_once |
| tests/integration/test_postgres_migrations.py | 549 | consume_once |
| tests/integration/test_postgres_migrations.py | 598 | append_event |
| tests/integration/test_postgres_migrations.py | 608 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 612 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 614 | consume_once |
| tests/integration/test_postgres_migrations.py | 627 | consume_once |
| tests/integration/test_postgres_migrations.py | 654 | append_event |
| tests/integration/test_postgres_migrations.py | 658 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 659 | consume_once |
| tests/integration/test_postgres_migrations.py | 694 | append_event |
| tests/integration/test_postgres_migrations.py | 695 | append_event |
| tests/integration/test_postgres_migrations.py | 698 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 710 | append_event |
| tests/integration/test_postgres_migrations.py | 714 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 725 | append_event |
| tests/integration/test_postgres_migrations.py | 732 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 747 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 790 | append_event |
| tests/integration/test_postgres_migrations.py | 2292 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2365 | append_event |
| tests/integration/test_postgres_migrations.py | 2368 | append_event |
| tests/integration/test_postgres_migrations.py | 2370 | append_event |
| tests/integration/test_postgres_migrations.py | 2373 | append_event |
| tests/integration/test_postgres_migrations.py | 2380 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2381 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2387 | consume_once |
| tests/integration/test_postgres_migrations.py | 2388 | consume_once |
| tests/integration/test_postgres_migrations.py | 2467 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2468 | consume_once |
| tests/integration/test_postgres_migrations.py | 2489 | append_event |
| tests/integration/test_postgres_migrations.py | 2528 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2554 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2555 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2559 | consume_once |
| tests/integration/test_postgres_migrations.py | 2593 | append_event |
| tests/integration/test_postgres_migrations.py | 2609 | append_event |
| tests/integration/test_postgres_migrations.py | 2648 | append_event |
| tests/integration/test_postgres_migrations.py | 2748 | append_event |
| tests/integration/test_postgres_migrations.py | 2774 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2831 | append_event |
| tests/integration/test_postgres_migrations.py | 2838 | append_event |
| tests/integration/test_postgres_migrations.py | 2906 | consume_once |
| tests/integration/test_postgres_migrations.py | 406 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 432 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 600 | append_event |
| tests/integration/test_postgres_migrations.py | 607 | append_event |
| tests/integration/test_postgres_migrations.py | 609 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 658 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2263 | append_event |
| tests/integration/test_postgres_migrations.py | 2382 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2394 | append_event |
| tests/integration/test_postgres_migrations.py | 2397 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2466 | append_event |
| tests/integration/test_postgres_migrations.py | 2497 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2520 | append_event |
| tests/integration/test_postgres_migrations.py | 2528 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2547 | append_event |
| tests/integration/test_postgres_migrations.py | 2548 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2554 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2555 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2556 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2687 | append_event |
| tests/integration/test_postgres_migrations.py | 2690 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2692 | append_event |
| tests/integration/test_postgres_migrations.py | 2852 | append_event |
| tests/integration/test_postgres_migrations.py | 2887 | append_event |
| tests/integration/test_postgres_migrations.py | 2895 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 348 | append_event |
| tests/integration/test_postgres_migrations.py | 2514 | dispatch_once |
| tests/integration/test_postgres_migrations.py | 2549 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2557 | LocalPublisher |
| tests/integration/test_postgres_migrations.py | 2516 | LocalPublisher |

Foram localizadas 41 chamadas explícitas de append_event; 41 pertencem a testes.
Os pontos de entrada de aplicação localizados ligam o dispatcher a LocalPublisher e o consumidor a apply_diagnostic_event. O evento aceito pela projeção é diagnostics.synthetic.created na versão 1.0.0.

### Fronteira de validação do produtor

append_event exige transação ativa e ambiente compatível; sua docstring recebe um EventEnvelope já validado. O corpo não chama o validador JSON Schema completo. Recomenda-se especificar a validação de schema como obrigação do produtor e testar essa obrigação antes de integrar cada produtor operacional.

### Identidade e recuperação

A Outbox controla event_id e identidade por versão. Recomenda-se aceitar a cardinalidade de um evento por versão apenas para o produtor sintético ensaiado. Cada produtor futuro deve confirmar a cardinalidade e a origem autoritativa para recuperação. Fixtures e resultados sintéticos fornecem a origem reproduzível do ensaio; a retenção oferece comprovante/hash, cuja suficiência para recuperar conteúdo precisa da fonte original.

### Consumidor lógico

consume_once deduplica por event_id em processed_event, com efeito e confirmação transacionais. A aplicação invoca apply_diagnostic_event. Recomenda-se aceitar um único consumidor lógico diagnóstico no I00; múltiplos processos desse mesmo consumidor permanecem sujeitos aos testes concorrentes. Consumidores independentes que precisam aplicar efeitos próprios exigem revisão da chave e da entrega.

## Decisões de escopo para revisão

1. Aprovar o mapeamento físico src/trade_system, apps/api e infrastructure para o recorte de TS-ST-001, documentando a correspondência com a estrutura proposta na Feature.
2. Confirmar o aceite de TS-ST-002 pelos dois envelopes v1 e seus exemplos/testes; registrar payloads de domínio e schema registry como cobertura remanescente de P61/P90.
3. Confirmar TS-ST-003 pelo produtor sintético ensaiado, com um evento por versão e validação completa antes de append_event. A origem de recuperação deve ser definida por produtor operacional ao integrá-lo.
4. Confirmar TS-ST-004 pelo publisher PostgreSQL local e um consumidor lógico diagnóstico. Integrações de transporte e consumidores independentes recebem revisão própria.

As decisões acima delimitam o recorte para revisão. O aceite técnico e o parecer QA permanecem dependentes dos responsáveis e das evidências aplicáveis.

## Aprovação das decisões de escopo

Aprovado o mapeamento físico existente com src/trade_system e apps/api para o recorte de TS-ST-001. A correspondência com a árvore proposta de I00-FEAT-001 fica documentada no inventário. As nove importações entre módulos identificadas aguardam revisão das fronteiras.

Confirmado o recorte de aceite de TS-ST-002 pelos dois envelopes CommandEnvelope v1 e EventEnvelope v1. Contratos de conteúdo de payload e schema registry permanecem como cobertura remanescente de P61/P90.

Confirmado o recorte de TS-ST-003 pelo produtor sintético ensaiado, com um evento por versão. Cada produtor operacional deverá ter validação completa do envelope antes de append_event e fonte autoritativa de recuperação definida ao ser integrado.

Confirmado o recorte de TS-ST-004 pelo publisher PostgreSQL local e um consumidor lógico diagnóstico. Consumidores independentes que precisam aplicar efeitos próprios exigem revisão da identidade de deduplicação e da entrega.