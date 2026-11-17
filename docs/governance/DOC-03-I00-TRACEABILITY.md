# Rastreabilidade DOC-03 para I00

Registro de 12/11/2026 em `IN_REVIEW`. As histórias e seus épicos constam no Blueprint, linhas 2019–2022. As pendências associadas aos épicos estão nas fichas de TS-EP-01 e TS-EP-02. O Engineering Foundation, na seção “Backlog refinado do I00”, refina as quatro histórias e acrescenta pacotes transversais. As relações pacote–critério–ADR técnica e os testes partem do registro mestre, com as atualizações da revisão do RC1.

O vínculo de um ID a um épico é **explícito** quando consta no Blueprint. A associação por conteúdo de uma pendência ou ADR de domínio a um pacote, teste ou componente é **proposta para revisão**. Ela delimita a cobertura observada e pode ser mais estreita que a pendência original. Pacotes transversais ficam identificados pelo ID I00. As histórias citadas como apoio nesses casos não representam uma atribuição histórica de backlog.

- [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)
- [Engineering Foundation original](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>)
- [Registro mestre de I00](../backlog/registro-mestre-i00.md) · [Critérios de aceite](../04-SEGURANCA-E-ACEITE.md)
- [Pendências reconciliadas](PENDING-ITEM-RECONCILIATION.md) · [ADRs reconciliadas](ADR-RECONCILIATION.md)
- [Manifesto e resultados históricos do RC1](../evidence/releases/i00-rc1/manifest.json) · [Resultados](../evidence/releases/i00-rc1/test-results.json) · [Revisão e aceite do bundle](../evidence/revisao-g0-i00-rc1.md)

## Histórias e pacotes

Os nomes de testes referem-se ao snapshot do commit candidato `8d1467d`, conferido no ZIP recuperado. Os critérios AC01–AC12 são de I00. As ADRs técnicas usam o prefixo TS-ADR na fonte. O componente indicado descreve o recorte técnico da entrega.

| História ou recorte | Pacote · aceite | Componente · contrato ou artefato | Pendências e ADRs de domínio relacionadas | ADR técnica ou decisão | Teste, verificação e evidência |
|---|---|---|---|---|---|
| TS-ST-001 · TS-EP-01 | I00-01 · AC01, AC10 | D07-C01 · estrutura modular | P85 · ADR-072, ADR-088 | 089, 090, 098 | `test_domain_package_is_importable`. [Bootstrap](../evidence/I00-bootstrap.md) |
| TS-ST-001 · TS-EP-01 | I00-02 · AC01, AC02 | D07-C01, D07-C02 · lockfile e toolchain | P85, P88 · ADR-072, ADR-073 | 094 | Instalação com lockfile, Ruff, mypy, pytest e build. [Bootstrap](../evidence/I00-bootstrap.md) |
| TS-ST-002 · TS-EP-01 | I00-03 · AC03, AC10 | D05-C02, D07-C02 · CommandEnvelope e EventEnvelope v1 | P90 (EP-01), P61 (EP-02, dependência temática) · ADR-052, ADR-073 | 097, 098 | `test_synthetic_example`, `test_required_fields`, `test_timestamps_require_valid_utc` e demais testes de schema. [Contratos](../evidence/I00-03-contratos.md) |
| TS-ST-003 · TS-EP-02 | I00-04 · AC04 | D05-C01 · PostgreSQL e Alembic | P48 · ADR-042 | 092, 095 | `test_migrations_round_trip`. [PostgreSQL](../evidence/I00-04-postgresql.md) |
| TS-ST-003 · TS-EP-02 | I00-05 · AC05, AC08 | D05-C01, D05-C02 · Outbox e EventEnvelope | P49, P50 · ADR-043–045 | 092, 093 | `test_outbox_commits_with_state`, `test_outbox_rolls_back_with_state`, `test_duplicate_event_rolls_back_new_state`. [Outbox](../evidence/I00-05-outbox.md) |
| TS-ST-004 · TS-EP-02 | I00-06 · AC07, AC08, AC09 | D05-C02 · fila e dispatcher | P50, P51 · ADR-044, ADR-045 | 090, 093, 096 | `test_dispatcher_orders_pending_versions_and_skips_locked_rows`, `test_dispatcher_retries_then_retains_failed_event`, `test_dispatcher_republishes_after_interruption`. [Dispatcher](../evidence/I00-06-dispatcher.md) |
| TS-ST-004 · TS-EP-02 | I00-07 · AC06, AC08 | D05-C02, D05-C06 · consumidor, deduplicação e projeção diagnóstica | P51, P60 · ADR-044, ADR-051 | 090, 093 | `test_duplicate_deliveries_apply_one_effect_across_restarts`, `test_consumer_rolls_back_effect_and_deduplication`. [Consumidor](../evidence/I00-07-consumidor.md) |
| API transversal | I00-08 · AC09, AC10 | API de diagnóstico local · OpenAPI gerado em runtime | P61 · interface de fundação. O vínculo com ADR-052 é indireto e passa pela decisão de versionamento de contratos | 091, 097, 098 | `test_health_and_info_work_without_database`, `test_openapi_declares_diagnostic_endpoints`, `test_api_readiness_requires_current_migrations`. [API](../evidence/I00-08-api.md) |
| Segurança transversal | I00-09 · AC10 | D06-C01, D06-C03, D06-C06 · configuração e restrições por ambiente | P63, P66, P69, mínimo de P70 · ADR-054, ADR-058 | 098 | `test_runtime_rejects_missing_or_invalid_policy`, `test_database_url_is_local_and_masks_password`, `test_workers_process_only_their_environment`, `test_postgres_rejects_live_events`. [Isolamento](../evidence/I00-09-isolamento.md) |
| Observabilidade transversal | I00-10 · AC09 | D05-C05, D06-C04 · correlação, logs e spans | P58, P75 · ADR-049, ADR-064 | 096 | `test_request_log_correlates_and_omits_secrets`, `test_correlation_traces_api_dispatcher_and_consumer`. [Telemetria](../evidence/I00-10-telemetria.md) |
| CI transversal · apoia TS-ST-001 | I00-11 · AC01, AC02 | D06-C02, D07-C02 · workflow e build | P72, P87, P88 · ADR-061, ADR-073 | 095 | CI histórico com lint, tipos, testes e build. [Resultados RC1](../evidence/releases/i00-rc1/test-results.json) |
| Governança transversal · apoia TS-EP-01 | I00-12 · AC11 | D07-C01 · registro mestre | P86, P87 · ADR-072 | T09 | Revisão documental dos vínculos e lacunas. [Rastreabilidade](../evidence/I00-12-rastreabilidade.md) |
| QA transversal · apoia TS-ST-004 | I00-13 · AC07, AC08 | D05-C02, D07-C05 · fila, retry e reinício | P51, recorte de P98 · ADR-044, ADR-081 | 093, 094 | `test_out_of_order_arrival_waits_for_missing_version`, `test_dispatcher_retry_recovers_after_publisher_unavailability`, `test_workers_restart_after_database_connection_failure`. [Resiliência](../evidence/I00-13-resiliencia.md) |
| Release transversal | I00-14 · AC11, AC12 | D06-C02, D07-C06 · Evidence Bundle RC1 | P101 · ADR-087 | T09 | Manifesto, oito hashes conferidos e aceite humano de 11/11. [Revisão RC1](../evidence/revisao-g0-i00-rc1.md) · [Conferência local](SOURCE-RECOVERY.md) · [Consolidação DOC-07](DOC-07-RC1-ACCEPTANCE.md) |

## Pendências vinculadas explicitamente aos épicos I00

| Pendências | Épico | Ligação I00 | Limite da evidência ou decisão em aberto |
|---|---|---|---|
| P66 | TS-EP-01 | I00-09 · conexão local e segregação lógica | Topologia, sub-redes, firewall e egress dependem de desenho e evidências do ambiente aplicável. |
| P68 | TS-EP-01 | I00-04 e I00-11 · Compose para PostgreSQL local e CI, conforme ADR-057 e TS-ADR-095 | Política de reinício e orquestração de runtime requerem decisão e teste próprios. O restart de workers em I00-13 exercita processos locais. |
| P85 | TS-EP-01 | TS-ST-001 · I00-01, I00-02, I00-11 | Build e imports históricos cobrem o bootstrap. A aplicação dos padrões ao restante do monorepo exige verificação por entrega. |
| P86 | TS-EP-01 | I00-12 · AC11 | Esta matriz amplia o vínculo inicial para I00. A associação global por ID permanece parcial. |
| P87 | TS-EP-01 | I00-11 e I00-12 · verificações de CI e governança | A aplicação da Definition of Done por entrega depende de registro de revisão e responsáveis. |
| P88 | TS-EP-01 | TS-ST-001 · I00-02, I00-11 | Toolchain e suítes iniciais têm evidência no RC1. A estratégia multicamadas segue por incremento. |
| P89 | TS-EP-01 | I00-02 · toolchain prevista na TS-ADR-094. Referência de domínio ADR-074 | Catálogo financeiro e cobertura property-based dependem dos fluxos aplicáveis. Sem evidência de aceite de P89 no RC1. |
| P90 | TS-EP-01 | TS-ST-002 · I00-03 | Testes cobrem envelopes v1 e exemplos sintéticos. Compatibilidade entre versões e contratos entre domínios exigem casos próprios. |
| P48, P49 | TS-EP-02 | TS-ST-003 · I00-04 e I00-05 | Migrações e atomicidade usam escopo sintético local. Ownership e limites de consistência por domínio exigem especificação e teste próprios. |
| P50 | TS-EP-02 | TS-ST-003 e TS-ST-004 · I00-05 a I00-07 | Modelo inicial de Outbox, dispatcher e consumidor local. Persistência e distribuição além desse recorte exigem desenho próprio. |
| P51 | TS-EP-02 | TS-ST-004 · I00-06, I00-07 e I00-13 | Há retenção após retries e espera pela versão ausente. Versões conflitantes, lacunas permanentes e tratamento de quarentena ficam em DOC-04. |
| P55 | TS-EP-02 | TS-ST-002 · I00-03 fornece validação de UTC no envelope | Temporalidade de mercado, disponibilidade e correções históricas requerem vínculo próprio com I01/I02 e evidência de recorte. |
| P56, P57 | TS-EP-02 | Sem história ou teste I00 específico localizado | Catálogo de features, normalização, versionamento e manifestos devem ser vinculados aos incrementos de features e treinamento. Confirmar a fronteira do épico antes de atribuir aceite I00. |
| P58 | TS-EP-02 | I00-10, com apoio de I00-08 e TS-ST-004 | Correlação em API, dispatcher e consumidor local. A trilha completa de operações exige verificação em fluxos de domínio. |
| P60 | TS-EP-02 | TS-ST-004 · I00-07 | A projeção diagnóstica dá evidência de efeito transacional idempotente. A reconstrução completa dos read models requer teste próprio. |
| P61 | TS-EP-02 | TS-ST-002 · I00-03, e I00-08 transversal | Schemas v1 e OpenAPI em runtime. Catálogo definitivo, schema registry, política de compatibilidade e contratos complementares requerem decisão e evidência. |
| P63 | TS-EP-02 | I00-09 · AC10 | Segregação lógica e rejeição de LIVE no contexto local. Criptografia e isolamento físico exigem fontes e verificações do ambiente correspondente. |

## P52 · Evolução da infraestrutura de eventos

Vínculo proposto com TS-ST-004 e I00-06/07/13, ADR-043/045 e TS-ADR-093. A Outbox, o dispatcher e os testes de retry, replay e deduplicação fornecem a referência inicial para comparar alternativas. P52 mantém M2. Falta aprovar critérios mensuráveis para adoção de broker, incluindo volume, atraso, recuperação e custo operacional, e produzir evidência comparável. [Dispatcher](../evidence/I00-06-dispatcher.md) · [Resiliência](../evidence/I00-13-resiliencia.md)

## Decisões e evidências ainda necessárias

| Assunto | O que falta | Encaminhamento |
|---|---|---|
| Associação formal de pendências e ADRs de domínio | O Blueprint registra os agrupamentos por épico. As ligações por pacote deste documento resultam do cruzamento de conteúdo. | Confirmar os vínculos no refinamento de I00 e indicar eventual registro mestre ou ata já aprovada. P69, P70, P72, P75, P98 e P101 são vínculos transversais por conteúdo. |
| API, segurança, telemetria, QA e governança transversais | As quatro histórias I00 são sementes de backlog e não identificam todos os pacotes transversais. TS-ST-020 e TS-ST-023 têm escopo posterior próprio. | Manter os IDs de pacote como referência de I00. Se for necessário formalizar histórias adicionais, registrar escopo e responsável no backlog. |
| DOC-04 · P51 · AC07 | Política e testes para conflito de versão e lacuna permanente, incluindo destino e tratamento de registros retidos. | Engenharia e QA precisam aprovar a [política proposta](DOC-04-OUTBOX-ORDERING.md) e validar os cenários pendentes. |
| [DOC-05](DOC-05-OUTBOX-METRICS.md) · P58, P75 · AC09 | Métricas propostas de backlog e atraso. | Aprovar definições e demonstrar medições em PostgreSQL no candidato. |
| DOC-06 · AC02 | Avaliação de compatibilidade e segurança do conjunto de dependências do candidato e responsável pela decisão. | Completar a [avaliação de dependências](DOC-06-RELEASE-DEPENDENCIES.md) com inventário, execução no candidato e decisão humana. |
| Atualidade da evidência | O ZIP RC1 contém testes como `test_correlation_traces_api_dispatcher_and_consumer` e `test_out_of_order_arrival_waits_for_missing_version` também localizados por nome no checkout oficial. O relatório de CI é do commit RC1. | Para afirmar cobertura atual, identificar o candidato atual, localizar testes equivalentes e obter CI ou execução rastreável. A evidência histórica mantém o escopo do RC1. |

DOC-03 tem cobertura inicial para as quatro histórias, 14 pacotes, 12 critérios e 19 pendências explicitamente agrupadas nos épicos de I00. P56 e P57 continuam sem verificação I00 específica. Seus vínculos posteriores estão na [matriz de I01 e I02](DOC-03-I01-I02-TRACEABILITY.md). G0 segue aberto.
