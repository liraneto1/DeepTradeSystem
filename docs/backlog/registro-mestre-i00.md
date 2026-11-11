# Registro mestre de I00

Referência em 11/11/2026. As baselines são `TS-ARCH-GLOBAL-V1.0` e
`TS-ENG-I00-V1.0`. O [backlog](../02-I00-BACKLOG.md) define as entregas e
dependências. Os [critérios de aceite](../04-SEGURANCA-E-ACEITE.md) e as
[ADRs técnicas](../05-ADRS-TECNICAS.md) definem as verificações e decisões.
A matriz usa `ACxx` para `I00-ACxx` e números de ADR para `TS-ADR-xxx`.
Os testes citados pelo nome estão na [suíte PostgreSQL](../../tests/integration/test_postgres_migrations.py).

## Pacotes e evidências

| Pacote | Requisito verificado | Critério | ADRs | Verificação | Evidência e estado |
|---|---|---|---|---|---|
| I00-01 | Estrutura e imports | AC01, AC10 | 089, 090, 098 | [Smoke de imports](../../tests/unit/test_package_imports.py) | Verificado · [evidência](../evidence/I00-bootstrap.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/09f15a9) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43068600483) |
| I00-02 | Instalação, lockfile e build | AC01, AC02 | 094 | Instalação `--locked`, Ruff, mypy, pytest e build | Verificado · [evidência](../evidence/I00-bootstrap.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/09f15a9) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43068600483) |
| I00-03 | Envelopes v1 | AC03, AC10 | 097, 098 | [Testes de schema](../../tests/contracts/test_envelope_schemas.py) | Verificado · [evidência](../evidence/I00-03-contratos.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/785ddd8) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43074607398) |
| I00-04 | PostgreSQL e migrations | AC04 | 092, 095 | `test_migrations_round_trip` | Verificado · [evidência](../evidence/I00-04-postgresql.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/d6a94d4) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43076038360) |
| I00-05 | Estado e Outbox atômicos | AC05, AC08 | 092, 093 | `test_outbox_commits_with_state`, `test_outbox_rolls_back_with_state` e `test_duplicate_event_rolls_back_new_state` | Verificado · [evidência](../evidence/I00-05-outbox.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/7b9e198) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43077559376) |
| I00-06 | Ordem de pendências, retries e publicação | AC07, AC08, AC09 | 090, 093, 096 | `test_dispatcher_orders_pending_versions_and_skips_locked_rows`, `test_dispatcher_retries_then_retains_failed_event` e `test_dispatcher_republishes_after_interruption` | Verificado · [evidência](../evidence/I00-06-dispatcher.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/5836638) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43079117165) |
| I00-07 | Deduplicação e efeito transacional | AC06, AC08 | 090, 093 | `test_duplicate_deliveries_apply_one_effect_across_restarts` e `test_consumer_rolls_back_effect_and_deduplication` | Verificado · [evidência](../evidence/I00-07-consumidor.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/5242876) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43080372348) |
| I00-08 | Saúde, prontidão e informações | AC09, AC10 | 091, 097, 098 | [Testes da API](../../tests/unit/test_diagnostic_api.py) e `test_api_readiness_requires_current_migrations` | Verificado · [evidência](../evidence/I00-08-api.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/4417a49) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43081582447) |
| I00-09 | Isolamento lógico e segredos | AC10 | 098 | [Testes de configuração](../../tests/unit/test_local_security.py), `test_workers_process_only_their_environment` e `test_postgres_rejects_live_events` | Verificado · [evidência](../evidence/I00-09-isolamento.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/95f2eb0) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43082587894) |
| I00-10 | Logs JSON, spans locais e correlação | AC09 | 096 | [Testes da API](../../tests/unit/test_diagnostic_api.py) e `test_correlation_traces_api_dispatcher_and_consumer` | Verificado · [evidência](../evidence/I00-10-telemetria.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/6504245) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43083964878) |
| I00-11 | CI de qualidade | AC01, AC02 | 095 | [Workflow](../../.github/workflows/ci.yml) | Verificado · [evidência](../evidence/I00-bootstrap.md) · [commit](https://github.com/liraneto1/DeepTradeSystem/commit/9ebfbdf) · [CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43068600483) |
| I00-12 | Registro mestre e lacunas rastreáveis | AC11 | T09, decisão da baseline técnica | Cobertura de IDs e verificação de referências | Entregue para revisão · [evidência](../evidence/I00-12-rastreabilidade.md) |
| I00-13 | Falhas e recuperação | AC07, AC08 | 093, 094 | `test_out_of_order_arrival_waits_for_missing_version`, `test_dispatcher_retry_recovers_after_publisher_unavailability` e `test_workers_restart_after_database_connection_failure` | Entregue para revisão · [evidência](../evidence/I00-13-resiliencia.md) |
| I00-14 | Evidence Bundle verificável | AC11, AC12 | T09, decisão da baseline técnica | Manifesto, hashes, release e decisão humana | Pendente · existem evidências por pacote |

Para I00-01 e I00-02, o CI vinculado é o primeiro verde após a correção de
I00-11. Para os demais pacotes verificados, os links apontam à execução
da entrega. A aprovação operacional dos gates exige decisão humana.

## Cobertura dos critérios de aceite

| Critério | Cobertura observada | Lacuna ou limite |
|---|---|---|
| I00-AC01 | Build e instalação repetidos no CI de I00-02 e I00-11. | O manifesto de release e seus hashes ficam em I00-14. |
| I00-AC02 | Dependências fixadas em [uv.lock](../../uv.lock) e instalação com `--locked`. | A avaliação de compatibilidade e segurança do conjunto de release permanece aberta em DOC-06. |
| I00-AC03 | Envelopes v1 e exemplos sintéticos validados em I00-03. | Regras dependentes de relógio, autorização e estado precisam de testes nos fluxos que as aplicarem. |
| I00-AC04 | Subida e reversão das migrations verificadas em PostgreSQL 17. | A evidência é de instância descartável no CI. |
| I00-AC05 | Estado e Outbox confirmados ou revertidos juntos em I00-05. | A evidência usa estado sintético. |
| I00-AC06 | Replay produz um único efeito após reiniciar o consumidor em I00-07. | A garantia observada vale para efeitos na mesma transação PostgreSQL. |
| I00-AC07 | Dispatcher preserva a ordem entre versões já pendentes do mesmo agregado em I00-06. | I00-13 valida o bloqueio até a chegada da versão anterior. Versões conflitantes e lacunas permanentes seguem em DOC-04. |
| I00-AC08 | Rollback, retry e recuperação após interrupção cobertos em I00-05 a I00-07. | I00-13 amplia a cobertura com retomada após indisponibilidade e reinício de processos. |
| I00-AC09 | Diagnóstico, logs JSON e correlação entre componentes em I00-08 e I00-10. | Métricas de backlog e atraso e sua evidência seguem em DOC-05. |
| I00-AC10 | Configuração inválida bloqueada, segregação lógica e LIVE rejeitado em I00-09. | A evidência se refere a TRAINING e PAPER em desenvolvimento local. |
| I00-AC11 | Pacotes, decisões, testes e evidências de I00 ligados nesta matriz. | A matriz global de ADRs, componentes, pendências, épicos e histórias segue em DOC-03. |
| I00-AC12 | Registros por pacote e hashes locais do bootstrap disponíveis. | Manifesto consolidado, identidade de release, integridade e aceite humano ficam em I00-14. |

## Lacunas e encaminhamentos

| ID | Estado | Próxima ação |
|---|---|---|
| DOC-01 | Aberta | Reconciliar P01–P47 com os originais D01–D04 do acervo local e registrar fonte por ID. A [visão inicial](../architecture/visao-inicial.md) aponta exemplos localizados. |
| DOC-02 | Aberta | Confirmar a classificação de P18. O domínio D02 identifica o tema de degradação e retreinamento. A classificação M3 segue provisória. |
| DOC-03 | Parcial | I00 está mapeado. Completar a relação global entre ADR, componente, pendência, épico, história, contrato, teste e evidência. Recuperar as fontes integrais das ADRs 001–088 e validar P01–P106 antes de publicar o vínculo global. |
| DOC-04 | Parcial | I00-13 valida a chegada tardia, retry e reinício. Definir reconciliação de versões conflitantes ou de lacunas que nunca recebem a versão anterior. |
| DOC-05 | Aberta | Definir e validar as métricas de backlog e atraso de Outbox previstas em T06. Registrar fonte, unidade e cenário de observação. |
| DOC-06 | Aberta | Registrar a avaliação de compatibilidade e segurança das dependências de release, owners nominais, capacidade e decisões pendentes sobre produção. |
| DOC-07 | Aberta | Consolidar o Evidence Bundle em I00-14. Registrar critérios quantitativos e decisões humanas sobre os gates quando aprovados. |

Os [riscos residuais da baseline](../06-PENDENCIAS-E-RASTREABILIDADE.md)
mantêm seus identificadores. As referências Word versionadas são
reconstruções. As fontes originais de arquitetura estão no acervo local.
