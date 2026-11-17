# Registro documental do Trade System V1

Auditoria TS-DOC-GOV de 12/11/2026. Status deste registro e dos demais entregáveis da auditoria: DRAFT, submetidos à revisão humana. O inventário abrange os arquivos documentais e de evidência de docs/ e contracts/, além das instruções e guias da raiz. Diretórios com apenas .gitkeep não contam como entregas. A criticidade alta indica material de baseline, contrato ou aceite. A média indica material de apoio. As associações por domínio e incremento são classificações de auditoria.

MISSING indica ausência no recorte local. DRAFT indica versão existente sem aceite específico registrado. IN_REVIEW indica decisão em aberto. APPROVED requer decisão humana identificável e vale para o objeto que a decisão nomeia. SUPERSEDED exige versão substituta identificada. Aprovação arquitetural, aprovação de pacote e aceite de release têm escopos distintos.

## Inventário local

| Arquivo | Domínio | Incremento | Criticidade | Estado | Evidência de aprovação |
|---|---|---|---|---|---|
| [AGENTS.md](../../../../AGENTS.md) | D01–D07 | I00–I09 | Alta | DRAFT | Instruções obrigatórias fornecidas pelo usuário. Sem registro de aprovação de versão localizado. |
| [command-envelope.example.json](../../../../contracts/examples/command-envelope.example.json) | D05, D07 | I00 | Alta | DRAFT | [Aceite do pacote I00-03](../../../evidence/releases/i00-rc1/manifest.json). Aprovação individual da versão não localizada. |
| [event-envelope.example.json](../../../../contracts/examples/event-envelope.example.json) | D05, D07 | I00 | Alta | DRAFT | [Aceite do pacote I00-03](../../../evidence/releases/i00-rc1/manifest.json). Aprovação individual da versão não localizada. |
| [command-envelope.v1.schema.json](../../../../contracts/jsonschema/command-envelope.v1.schema.json) | D05, D07 | I00 | Alta | DRAFT | [Aceite do pacote I00-03](../../../evidence/releases/i00-rc1/manifest.json). Aprovação individual da versão não localizada. |
| [event-envelope.v1.schema.json](../../../../contracts/jsonschema/event-envelope.v1.schema.json) | D05, D07 | I00 | Alta | DRAFT | [Aceite do pacote I00-03](../../../evidence/releases/i00-rc1/manifest.json). Aprovação individual da versão não localizada. |
| [00-BASELINE-E-ESCOPO.md](../../../00-BASELINE-E-ESCOPO.md) | D01–D07 | I00–I09 | Alta | DRAFT | Aprovação da baseline declarada. Consolidação local. |
| [01-ARQUITETURA-FISICA.md](../../../01-ARQUITETURA-FISICA.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [02-I00-BACKLOG.md](../../../02-I00-BACKLOG.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [03-CONTRATOS.md](../../../03-CONTRATOS.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [04-SEGURANCA-E-ACEITE.md](../../../04-SEGURANCA-E-ACEITE.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [05-ADRS-TECNICAS.md](../../../05-ADRS-TECNICAS.md) | D05–D07 | I00 | Alta | DRAFT | Decisões 089–098 registradas como aprovadas. Resumos locais. |
| [06-PENDENCIAS-E-RASTREABILIDADE.md](../../../06-PENDENCIAS-E-RASTREABILIDADE.md) | D01–D07 | I00–I09 | Alta | DRAFT | Sem aceite específico localizado |
| [visao-geral.png](../../../architecture/visao-geral.png) | D01–D07 | I00–I09 | Média | DRAFT | Sem aceite específico localizado |
| [visao-inicial.md](../../../architecture/visao-inicial.md) | D01–D07 | I00–I09 | Média | DRAFT | Sem aceite específico localizado |
| [registro-mestre-i00.md](../../../backlog/registro-mestre-i00.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-03-contratos.md](../../../evidence/I00-03-contratos.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-04-postgresql.md](../../../evidence/I00-04-postgresql.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-05-outbox.md](../../../evidence/I00-05-outbox.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-06-dispatcher.md](../../../evidence/I00-06-dispatcher.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-07-consumidor.md](../../../evidence/I00-07-consumidor.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-08-api.md](../../../evidence/I00-08-api.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-09-isolamento.md](../../../evidence/I00-09-isolamento.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-10-telemetria.md](../../../evidence/I00-10-telemetria.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-12-rastreabilidade.md](../../../evidence/I00-12-rastreabilidade.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-13-resiliencia.md](../../../evidence/I00-13-resiliencia.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I00-bootstrap.md](../../../evidence/I00-bootstrap.md) | D05–D07 | I00 | Alta | DRAFT | Sem aceite específico localizado |
| [I01-consolidacao.md](../../../evidence/I01-consolidacao.md) | D01, D05, D07 | I01 | Alta | DRAFT | [Aceite da ingestão contínua](../../../evidence/I01-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I01-historico-btcusdt.md](../../../evidence/I01-historico-btcusdt.md) | D01, D05, D07 | I01 | Alta | DRAFT | [Aceite da ingestão contínua](../../../evidence/I01-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I01-ingestao-continua-btcusdt.md](../../../evidence/I01-ingestao-continua-btcusdt.md) | D01, D05, D07 | I01 | Alta | DRAFT | [Aceite da ingestão contínua](../../../evidence/I01-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I01-persistencia-btcusdt.md](../../../evidence/I01-persistencia-btcusdt.md) | D01, D05, D07 | I01 | Alta | DRAFT | [Aceite da ingestão contínua](../../../evidence/I01-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I02-consolidacao.md](../../../evidence/I02-consolidacao.md) | D01, D05, D07 | I02 | Alta | DRAFT | [Aceite dos recortes I02](../../../evidence/I02-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I02-features-adicionais.md](../../../evidence/I02-features-adicionais.md) | D01, D05, D07 | I02 | Alta | DRAFT | [Aceite dos recortes I02](../../../evidence/I02-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I02-market-state-inicial.md](../../../evidence/I02-market-state-inicial.md) | D01, D05, D07 | I02 | Alta | DRAFT | [Aceite dos recortes I02](../../../evidence/I02-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I02-market-state-multi-intervalo.md](../../../evidence/I02-market-state-multi-intervalo.md) | D01, D05, D07 | I02 | Alta | DRAFT | [Aceite dos recortes I02](../../../evidence/I02-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [I03-custos-paper.md](../../../evidence/I03-custos-paper.md) | D03, D05, D07 | I03 | Alta | DRAFT | Sem aceite específico localizado |
| [I03-futures-paper.md](../../../evidence/I03-futures-paper.md) | D03, D05, D07 | I03 | Alta | DRAFT | Sem aceite específico localizado |
| [I03-market-state-paper.md](../../../evidence/I03-market-state-paper.md) | D03, D05, D07 | I03 | Alta | DRAFT | Sem aceite específico localizado |
| [I03-persistencia-paper.md](../../../evidence/I03-persistencia-paper.md) | D03, D05, D07 | I03 | Alta | DRAFT | Sem aceite específico localizado |
| [.gitattributes](../../../evidence/releases/i00-rc1/.gitattributes) | D05–D07 | I00 | Alta | DRAFT | Metadado auxiliar. Sem aceite específico localizado. |
| [diagnostic-log.json](../../../evidence/releases/i00-rc1/diagnostic-log.json) | D05–D07 | I00 | Alta | APPROVED | [Aceite do bundle RC1 em 11/11](../../../evidence/revisao-g0-i00-rc1.md). Escopo da aprovação é o bundle histórico. |
| [manifest.json](../../../evidence/releases/i00-rc1/manifest.json) | D05–D07 | I00 | Alta | APPROVED | [Aceite do bundle RC1 em 11/11](../../../evidence/revisao-g0-i00-rc1.md). Escopo da aprovação é o bundle histórico. |
| [README.md](../../../evidence/releases/i00-rc1/README.md) | D05–D07 | I00 | Alta | APPROVED | [Aceite do bundle RC1 em 11/11](../../../evidence/revisao-g0-i00-rc1.md). Escopo da aprovação é o bundle histórico. |
| [test-results.json](../../../evidence/releases/i00-rc1/test-results.json) | D05–D07 | I00 | Alta | APPROVED | [Aceite do bundle RC1 em 11/11](../../../evidence/revisao-g0-i00-rc1.md). Escopo da aprovação é o bundle histórico. |
| [revisao-g0-i00-rc1.md](../../../evidence/revisao-g0-i00-rc1.md) | D05–D07 | I00–I04 | Alta | IN_REVIEW | Registro de aceite de I00-14 e avaliação técnica de G0. Decisão de G0 pendente. |
| [LEIA-ME.md](../../../referencias/LEIA-ME.md) | D01–D07 | I00–I09 | Média | DRAFT | Sem aceite específico localizado |
| [D01 oficial](<../../../referencias/originais/Domínio 01 - Integração e Dados de Mercado.txt>) | D01 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [D02 oficial](<../../../referencias/originais/Domínio 02 - Inteligência Artificial e Aprendizado.txt>) | D02 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [D03 oficial](<../../../referencias/originais/Domínio 03 - Risco, Execução e Controle Operacional.txt>) | D03 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [D04 oficial](<../../../referencias/originais/Domínio 04 - Plataforma de Operações e Observabilidade.txt>) | D04 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [D05 oficial](<../../../referencias/originais/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt>) | D05 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [D06 oficial](<../../../referencias/originais/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>) | D06 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [D07 oficial](<../../../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) | D07 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [GLOBAL oficial](<../../../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) | D01–D07 | I00–I09 | Alta | APPROVED | Fonte oficial confirmada pelo usuário em 16/11/2026. |
| [api-diagnostico.md](../../../runbooks/api-diagnostico.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [consumidor-idempotente.md](../../../runbooks/consumidor-idempotente.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [dispatcher-outbox.md](../../../runbooks/dispatcher-outbox.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [historico-btcusdt.md](../../../runbooks/historico-btcusdt.md) | D01, D05, D07 | I01 | Média | DRAFT | [Aceite da ingestão contínua](../../../evidence/I01-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [ingestao-continua-btcusdt.md](../../../runbooks/ingestao-continua-btcusdt.md) | D01, D05, D07 | I01 | Média | DRAFT | [Aceite da ingestão contínua](../../../evidence/I01-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [isolamento-e-segredos.md](../../../runbooks/isolamento-e-segredos.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [market-state-btcusdt.md](../../../runbooks/market-state-btcusdt.md) | D01, D05, D07 | I02 | Média | DRAFT | [Aceite dos recortes I02](../../../evidence/I02-consolidacao.md). Aprovação individual do arquivo não localizada. |
| [outbox-transacional.md](../../../runbooks/outbox-transacional.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [paper-futures.md](../../../runbooks/paper-futures.md) | D03, D05, D07 | I03 | Média | DRAFT | Sem aceite específico localizado |
| [paper-livro-razao.md](../../../runbooks/paper-livro-razao.md) | D03, D05, D07 | I03 | Média | DRAFT | Sem aceite específico localizado |
| [paper-market-state.md](../../../runbooks/paper-market-state.md) | D03, D05, D07 | I03 | Média | DRAFT | Sem aceite específico localizado |
| [paper-simulacao-inicial.md](../../../runbooks/paper-simulacao-inicial.md) | D03, D05, D07 | I03 | Média | DRAFT | Sem aceite específico localizado |
| [paper-taxas-e-slippage.md](../../../runbooks/paper-taxas-e-slippage.md) | D03, D05, D07 | I03 | Média | DRAFT | Sem aceite específico localizado |
| [postgresql-local.md](../../../runbooks/postgresql-local.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [revisao-vscode.md](../../../runbooks/revisao-vscode.md) | D01–D07 | I00–I09 | Média | DRAFT | Sem aceite específico localizado |
| [telemetria-local.md](../../../runbooks/telemetria-local.md) | D05–D07 | I00 | Média | DRAFT | Sem aceite específico localizado |
| [PROMPT-INICIAL-CODEX.md](../../../../PROMPT-INICIAL-CODEX.md) | D01–D07 | I00–I09 | Média | DRAFT | Sem aceite específico localizado |
| [README.md](../../../../README.md) | D01–D07 | I00–I09 | Média | DRAFT | Sem aceite específico localizado |

## Recuperação posterior à auditoria

| Item | Domínio | Incremento | Criticidade | Estado | Evidência ou fonte |
|---|---|---|---|---|---|
| SHA256SUMS e artefatos de build RC1 | D06–D07 | I00 | Alta | APPROVED | Bundle aceito em 11/11. Oito hashes verificados no checkout em 12/11. |
| Originais do Blueprint, Engineering Foundation e D01–D07 | D01–D07 | I00–I09 | Alta | IN_REVIEW | Fontes recuperadas. Aprovação das decisões registrada nas seções finais do Blueprint e do Engineering Foundation. [Procedência](../../SOURCE-RECOVERY.md) |
| Registros de reconciliação de P01–P106 e ADR-001–098 | D01–D07 | I00–I09 | Alta | IN_REVIEW | As descrições, fases e decisões têm fontes por ID. [Pendências](../../PENDING-ITEM-RECONCILIATION.md) · [ADRs](../../ADR-RECONCILIATION.md) · [Ressalvas](../../RECONCILIATION-DECISIONS.md) |
| Matriz de rastreabilidade DOC-03 | D05–D07 | I00 | Alta | IN_REVIEW | Vínculos de quatro histórias, 14 pacotes e 19 pendências dos épicos. Resultados históricos vinculados ao RC1. [Matriz I00](../../DOC-03-I00-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D01, D05 | I01–I02 | Alta | IN_REVIEW | Vínculos de TS-ST-005–008 e recorte de P56 e P57. Resultados históricos e verificações locais identificados. [Matriz I01 e I02](../../DOC-03-I01-I02-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D03, D05, D07 | I03 | Alta | IN_REVIEW | Vínculos de TS-ST-009–012, testes Spot atuais e evidências históricas do Trading Core PAPER. [Matriz I03](../../DOC-03-I03-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D01–D03, D05, D07 | I04 | Alta | IN_REVIEW | Vínculos de TS-ST-013/014 e recorte de P56 e P57. Evidências de dependências identificadas. [Matriz I04](../../DOC-03-I04-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D02, D03, D05, D07 | I05 | Alta | IN_REVIEW | Vínculos de TS-ST-015/016, P57 e pendências de backtest, walk-forward, benchmarks e G1. [Matriz I05](../../DOC-03-I05-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D03–D05, D07 | I06 | Alta | IN_REVIEW | Vínculos de TS-ST-017–020, evidências de dependência e condições pendentes de G2. [Matriz I06](../../DOC-03-I06-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D03, D05–D07 | I07 | Alta | IN_REVIEW | Vínculos de TS-ST-021/022 e condições pendentes de G3. [Matriz I07](../../DOC-03-I07-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D06, D07 | I08 | Alta | IN_REVIEW | Vínculos de TS-ST-023, Evidence Bundle e condições pendentes de G4. [Matriz I08](../../DOC-03-I08-TRACEABILITY.md) |
| Matriz de rastreabilidade DOC-03 | D06, D07 | I09 | Alta | IN_REVIEW | Vínculos de TS-ST-024, evidências de dependência e condições pendentes de G5. [Matriz I09](../../DOC-03-I09-TRACEABILITY.md) |
| Consolidação DOC-03 | D01–D07 | I00–I09 | Alta | IN_REVIEW | 24 histórias iniciais, evidências e validações pendentes de G0–G5. [Consolidação](../../DOC-03-CONSOLIDATION.md) |
| Critérios de aceite de AC02 para engenharia | D06, D07 | I00 | Alta | APPROVED | Critérios aprovados pelo usuário em 12/11/2026 nesta conversa. [Critérios](../../AC02-ENGINEERING-ACCEPTANCE.md) |
| Repasse de AC02 para engenharia | D06, D07 | I00 | Alta | IN_REVIEW | Execução e evidências pendentes para imagem PostgreSQL, componentes nativos e build Linux. [Repasse](../../AC02-ENGINEERING-HANDOFF.md) |
| Dossiê de revisão de G0 | D01–D07 | I00–I04 | Alta | IN_REVIEW | Evidências, ressalvas e decisão humana pendente. [Dossiê](../../G0-REVIEW-DOSSIER.md) |
| Visão de arquitetura do Trading Core PAPER | D03, D05 | I03 | Alta | DRAFT | Baseada no Blueprint, em D03 e na matriz de I03. Decisões abertas estão registradas na [visão de arquitetura](../../../architecture/trading-core-paper.md). |
| Especificação de Control e Risk PAPER | D03 | I03 | Alta | DRAFT | Regras de TS-ST-009/010 vinculadas a D03, à visão de arquitetura e à matriz de I03. [Especificação](../../../domains/d03-control-risk-paper.md) |
| Especificação de execução simulada e reconciliação do Portfolio PAPER | D03, D05 | I03 | Alta | DRAFT | Regras de TS-ST-011/012 vinculadas a D03, à visão de arquitetura e à matriz de I03. [Especificação](../../../domains/d03-execution-portfolio-paper.md) |
| Registros individuais ADR-089–098 | D05–D07 | I00 | Alta | MISSING | Resumos das decisões em docs/05. |
| Especificações de domínio e componentes para desenvolvimento | D01–D07 | Conforme incremento | Alta | MISSING | Reconstruções descrevem componentes lógicos. Suficiência deve ser confirmada por história. |
| OpenAPI versionado, ErrorEnvelope.v1, HealthStatus.v1 e OutboxRecord.v1 | D05–D07 | I00 | Alta | MISSING | OpenAPI gerado pela API é citado nas evidências. As demais definições são propostas em docs/03. Confirmar quais exigem publicação como artefato. |
| Documentação desta auditoria | D01–D07 | I00–I09 | Alta | DRAFT | Quatro arquivos em docs/governance, aguardando validação do catálogo e das prioridades. |

A confirmação das fontes oficiais de 16/11/2026 também abrange o [Engineering Foundation](<../../../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>).


## Complemento do inventário · 16/11/2026

Arquivos localizados sem link direto na edição anterior. A existência aqui registra disponibilidade para revisão. O escopo e o estado de cada decisão constam do [Approval Register](../../APPROVAL-REGISTER.md). O [TS-DOC-STD-V1.0 e seus sete templates](../../TS-DOC-STD-V1.0.md) estão APPROVED desde 16/11/2026. O usuário também aprovou a classificação dos [bloqueios de I00 para G0](../../GAP-REGISTER.md).

- [docs/adr/ADR-017.md](<../../../adr/ADR-017.md>)
- [docs/adr/ADR-018.md](<../../../adr/ADR-018.md>)
- [docs/adr/ADR-019.md](<../../../adr/ADR-019.md>)
- [docs/adr/ADR-020.md](<../../../adr/ADR-020.md>)
- [docs/adr/ADR-021.md](<../../../adr/ADR-021.md>)
- [docs/adr/ADR-022.md](<../../../adr/ADR-022.md>)
- [docs/adr/ADR-023.md](<../../../adr/ADR-023.md>)
- [docs/adr/ADR-024.md](<../../../adr/ADR-024.md>)
- [docs/adr/ADR-025.md](<../../../adr/ADR-025.md>)
- [docs/adr/ADR-026.md](<../../../adr/ADR-026.md>)
- [docs/adr/ADR-027.md](<../../../adr/ADR-027.md>)
- [docs/adr/ADR-028.md](<../../../adr/ADR-028.md>)
- [docs/adr/README.md](<../../../adr/README.md>)
- [docs/evidence/AC02-d561026-digest-triage.md](<../../../evidence/AC02-d561026-digest-triage.md>)
- [docs/evidence/AC02-d561026-linux-security.md](<../../../evidence/AC02-d561026-linux-security.md>)
- [docs/evidence/AC02-d561026-linux-wheel-static.json](<../../../evidence/AC02-d561026-linux-wheel-static.json>)
- [docs/evidence/AC02-d561026-postgres-triage.csv](<../../../evidence/AC02-d561026-postgres-triage.csv>)
- [docs/evidence/AC02-d561026-retorno-engenharia.md](<../../../evidence/AC02-d561026-retorno-engenharia.md>)
- [docs/evidence/AC02-d561026.json](<../../../evidence/AC02-d561026.json>)
- [docs/evidence/AC02-postgres-6f7593c-trivy.json](<../../../evidence/AC02-postgres-6f7593c-trivy.json>)
- [docs/evidence/AC07-11e61c9-outbox.md](<../../../evidence/AC07-11e61c9-outbox.md>)
- [docs/evidence/AC07-autorizacao-outbox.md](<../../../evidence/AC07-autorizacao-outbox.md>)
- [docs/evidence/AC07-autorizacao-sha256.txt](<../../../evidence/AC07-autorizacao-sha256.txt>)
- [docs/evidence/AC07-conflito-concorrente-outbox.md](<../../../evidence/AC07-conflito-concorrente-outbox.md>)
- [docs/evidence/AC07-consolidacao-aceite-tecnico.md](<../../../evidence/AC07-consolidacao-aceite-tecnico.md>)
- [docs/evidence/AC07-consulta-colisoes-legadas.sql](<../../../evidence/AC07-consulta-colisoes-legadas.sql>)
- [docs/evidence/AC07-dispatcher-login-restrito.md](<../../../evidence/AC07-dispatcher-login-restrito.md>)
- [docs/evidence/AC07-dispatcher-login-sha256.txt](<../../../evidence/AC07-dispatcher-login-sha256.txt>)
- [docs/evidence/AC07-escalonamento-predecessor.md](<../../../evidence/AC07-escalonamento-predecessor.md>)
- [docs/evidence/AC07-escalonamento-sha256.txt](<../../../evidence/AC07-escalonamento-sha256.txt>)
- [docs/evidence/AC07-event-id-divergente.md](<../../../evidence/AC07-event-id-divergente.md>)
- [docs/evidence/AC07-event-id-sha256.txt](<../../../evidence/AC07-event-id-sha256.txt>)
- [docs/evidence/AC07-parametros-operacionais.md](<../../../evidence/AC07-parametros-operacionais.md>)
- [docs/evidence/AC07-parametros-sha256.txt](<../../../evidence/AC07-parametros-sha256.txt>)
- [docs/evidence/AC07-produtores-e-colisoes-legadas.md](<../../../evidence/AC07-produtores-e-colisoes-legadas.md>)
- [docs/evidence/AC07-quarentena-retomada.md](<../../../evidence/AC07-quarentena-retomada.md>)
- [docs/evidence/AC07-quarentena-sha256.txt](<../../../evidence/AC07-quarentena-sha256.txt>)
- [docs/evidence/AC09-11e61c9-outbox.md](<../../../evidence/AC09-11e61c9-outbox.md>)
- [docs/evidence/AC09-coletor-outbox.md](<../../../evidence/AC09-coletor-outbox.md>)
- [docs/evidence/AC09-outbox-metrics-sha256.txt](<../../../evidence/AC09-outbox-metrics-sha256.txt>)
- [docs/evidence/I03-funding-automatico-paper.md](<../../../evidence/I03-funding-automatico-paper.md>)
- [docs/evidence/I03-funding-paper.md](<../../../evidence/I03-funding-paper.md>)
- [docs/evidence/I03-liquidacao-automatica-paper.md](<../../../evidence/I03-liquidacao-automatica-paper.md>)
- [docs/evidence/I03-liquidacao-paper.md](<../../../evidence/I03-liquidacao-paper.md>)
- [docs/evidence/I03-market-state-futures-paper.md](<../../../evidence/I03-market-state-futures-paper.md>)
- [docs/evidence/I03-recuperacao-marcacao-paper.md](<../../../evidence/I03-recuperacao-marcacao-paper.md>)
- [docs/evidence/I03-replay-liquidacao-paper.md](<../../../evidence/I03-replay-liquidacao-paper.md>)
- [docs/evidence/releases/i00-rc1/SHA256SUMS](<../../../evidence/releases/i00-rc1/SHA256SUMS>)
- [docs/governance/APPROVAL-REGISTER.md](<../../APPROVAL-REGISTER.md>)
- [docs/governance/AUDITORIA-DOCUMENTAL-I00.md](<../../AUDITORIA-DOCUMENTAL-I00.md>)
- [docs/governance/DOC-04-OUTBOX-ORDERING.md](<../../DOC-04-OUTBOX-ORDERING.md>)
- [docs/governance/DOC-05-OUTBOX-METRICS.md](<../../DOC-05-OUTBOX-METRICS.md>)
- [docs/governance/DOC-06-RELEASE-DEPENDENCIES.md](<../../DOC-06-RELEASE-DEPENDENCIES.md>)
- [docs/governance/DOC-07-RC1-ACCEPTANCE.md](<../../DOC-07-RC1-ACCEPTANCE.md>)
- [docs/governance/DOCUMENT-GAP-ANALYSIS.md](<../../DOCUMENT-GAP-ANALYSIS.md>)
- [docs/governance/DOCUMENT-REGISTRY.md](<../../DOCUMENT-REGISTRY.md>)
- [docs/governance/DOCUMENTATION-ROADMAP.md](<../../DOCUMENTATION-ROADMAP.md>)
- [docs/governance/GAP-REGISTER.md](<../../GAP-REGISTER.md>)
- [docs/governance/REQUIREMENTS-TRACEABILITY-MATRIX.md](<../../REQUIREMENTS-TRACEABILITY-MATRIX.md>)
- [docs/governance/templates/CONTRATO.md](<../../templates/CONTRATO.md>)
- [docs/governance/templates/EPICO.md](<../../templates/EPICO.md>)
- [docs/governance/templates/EVIDENCIA.md](<../../templates/EVIDENCIA.md>)
- [docs/governance/templates/FEATURE.md](<../../templates/FEATURE.md>)
- [docs/governance/templates/HISTORIA-TECNICA.md](<../../templates/HISTORIA-TECNICA.md>)
- [docs/governance/templates/INCREMENTO.md](<../../templates/INCREMENTO.md>)
- [docs/governance/templates/TESTE.md](<../../templates/TESTE.md>)
- [docs/governance/TS-DOC-STD-V1.0.md](<../../TS-DOC-STD-V1.0.md>)
- [docs/referencias/Architecture & MVP Blueprint.txt](<../../../referencias/Architecture & MVP Blueprint.txt>)
- [docs/referencias/Binance API Integration.txt](<../../../referencias/Binance API Integration.txt>)
- [docs/referencias/Domínio 01 - Integração e Dados de Mercado.txt](<../../../referencias/Domínio 01 - Integração e Dados de Mercado.txt>)
- [docs/referencias/Domínio 02 - Inteligência Artificial e Aprendizado.txt](<../../../referencias/Domínio 02 - Inteligência Artificial e Aprendizado.txt>)
- [docs/referencias/Domínio 03 - Risco, Execução e Controle Operacional.txt](<../../../referencias/Domínio 03 - Risco, Execução e Controle Operacional.txt>)
- [docs/referencias/Domínio 04 - Plataforma de Operações e Observabilidade.txt](<../../../referencias/Domínio 04 - Plataforma de Operações e Observabilidade.txt>)
- [docs/referencias/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt](<../../../referencias/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt>)
- [docs/referencias/Domínio 06 · Infraestrutura, Segurança e DevOps.txt](<../../../referencias/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>)
- [docs/referencias/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt](<../../../referencias/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>)
- [docs/referencias/Trading Operations Viewer.txt](<../../../referencias/Trading Operations Viewer.txt>)
- [docs/referencias/TS-ENG-I00-V1.0 - Engineering Foundation.txt](<../../../referencias/TS-ENG-I00-V1.0 - Engineering Foundation.txt>)
- [docs/TS-DOC-STD-V1.0.txt](<../../../TS-DOC-STD-V1.0.txt>)
