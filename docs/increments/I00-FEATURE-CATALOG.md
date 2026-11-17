# I00-FEATURE-CATALOG.md
## TRADE SYSTEM V1 — I00 Feature Catalog

**Document ID:** TS-I00-FEAT-CAT-001  
**Version:** 1.0  
**Status:** APPROVED  
**Increment:** I00 — Engineering Foundation  
**Primary Domains:** D05 / D06 / D07  
**Owner:** Engineering Architecture & Documentation Governance  
**Architecture Baseline:** TS-ARCH-GLOBAL-V1.0 — APPROVED  
**Engineering Baseline:** TS-ENG-I00-V1.0 — APPROVED  
**Increment Baseline:** TS-INC-I00-001 — APPROVED  
**Epic References:** TS-EP-01 / V1.0; TS-EP-02 / V1.0 — APPROVED  
**Feature Template:** TS-DOC-TPL-FEAT-001 — APPROVED  
**Traceability Matrix:** TS-DOC-TRC-001 — APPROVED  
**Gap Register:** TS-DOC-GAP-001 — APPROVED  
**Approval Reference:** [16/11/2026 · aprovação sem ressalvas](../governance/history/TS-I00-FEAT-CAT-001/APPROVAL.md)  
**Domain:** D05 / D06 / D07  
**Source References:** [anexo original](../governance/history/TS-I00-FEAT-CAT-001/IN-REVIEW.txt), [TS-DOC-STD-V1.0](../governance/TS-DOC-STD-V1.0.md) e [fontes oficiais](../referencias/originais/)  
**Related ADRs:** referências da seção 8.  
**Related Components:** vínculos da seção 8 e [DOC-03 I00](../governance/DOC-03-I00-TRACEABILITY.md).  
**Related Requirements/Pendências:** critérios I00 e lacunas aplicáveis, conforme seções 9 e 11.  
**Dependencies:** [I00](I00-INCREMENT.md), [TS-EP-01](../epics/TS-EP-01.md), [TS-EP-02](../epics/TS-EP-02.md) e [template de Feature](../governance/templates/FEATURE-TEMPLATE.md). Dependências entre Features na seção 6.  
**Acceptance Criteria:** seção 9 para o catálogo, seções 10 e 13 para prontidão e aceite da implementação.  
**Last Updated:** 2026-11-16

---

## 1. Objetivo

Formalizar o catálogo das Features planejadas para o incremento I00, permitindo decompor os dois épicos aprovados em capacidades técnicas coesas, rastreáveis e verificáveis.

O catálogo deverá:

- Estabelecer identificadores estáveis.
- Definir ownership funcional inicial.
- Delimitar escopos e fronteiras.
- Relacionar pacotes de trabalho.
- Identificar dependências.
- Estabelecer critérios de aceite de alto nível.
- Referenciar histórias e contratos.
- Registrar lacunas.
- Orientar o refinamento das especificações individuais.

A aprovação do catálogo não significa que as Features estejam documentalmente READY ou implementadas.

## 2. Regras do catálogo

1. Cada Feature deverá possuir um identificador único `I00-FEAT-NNN`.
2. Cada Feature terá um épico principal.
3. Relações com outros épicos serão permitidas.
4. Um pacote de trabalho poderá contribuir para mais de uma Feature.
5. Uma Feature poderá possuir múltiplas histórias.
6. Histórias já aprovadas deverão preservar seus identificadores.
7. Não serão criados requisitos ou ADRs por inferência.
8. Critérios de aceite específicos serão detalhados nas especificações individuais.
9. Lacunas bloqueantes deverão impedir o READY das entregas dependentes.
10. Mudanças materiais após aprovação deverão seguir Change Control.

## 3. Catálogo mestre das Features

| Feature ID | Feature | Épico principal | Work Package |
|---|---|---|---|
| I00-FEAT-001 | Monorepo Bootstrap | TS-EP-01 | I00-01 |
| I00-FEAT-002 | Python Toolchain & Quality | TS-EP-01 | I00-02 |
| I00-FEAT-003 | Versioned Contracts | TS-EP-01 | I00-03 |
| I00-FEAT-004 | PostgreSQL & Migrations | TS-EP-02 | I00-04 |
| I00-FEAT-005 | Transactional Outbox | TS-EP-02 | I00-05 |
| I00-FEAT-006 | Event Dispatcher | TS-EP-02 | I00-06 |
| I00-FEAT-007 | Idempotent Consumers | TS-EP-02 | I00-07 |
| I00-FEAT-008 | Foundation API | TS-EP-01 | I00-08 |
| I00-FEAT-009 | Security & Environment Isolation | TS-EP-01 | I00-09 |
| I00-FEAT-010 | Observability Foundation | TS-EP-01 | I00-10 |
| I00-FEAT-011 | CI/CD Foundation | TS-EP-01 | I00-11 |
| I00-FEAT-012 | Documentation & Traceability | TS-EP-01 | I00-12 |
| I00-FEAT-013 | Failure & Recovery Validation | TS-EP-02 | I00-13 |
| I00-FEAT-014 | Evidence & G0 Preparation | TS-EP-01 | I00-14 |

**Estado inicial:** PROPOSED.

A distribuição segue as propostas registradas nas especificações aprovadas do I00 e dos épicos.

O catálogo deverá ser aprovado antes que essa distribuição seja considerada normativa.

## 4. Distribuição por épico

### TS-EP-01 — Engineering Foundation

Features:

- I00-FEAT-001.
- I00-FEAT-002.
- I00-FEAT-003.
- I00-FEAT-008.
- I00-FEAT-009.
- I00-FEAT-010.
- I00-FEAT-011.
- I00-FEAT-012.
- I00-FEAT-014.

Total: 9 Features.

### TS-EP-02 — Data & Event Foundation

Features:

- I00-FEAT-004.
- I00-FEAT-005.
- I00-FEAT-006.
- I00-FEAT-007.
- I00-FEAT-013.

Total: 5 Features.

As Features de contratos, segurança, observabilidade, recuperação e evidências possuem responsabilidades transversais, embora tenham um único épico principal.

## 5. Especificações resumidas

### I00-FEAT-001 — Monorepo Bootstrap

**Épico:** TS-EP-01  
**Pacote:** I00-01  
**Domínio principal proposto:** D07

**Objetivo:** estabelecer a estrutura modular do repositório.

**Escopo:** organização de módulos, convenções, estrutura de testes, configuração inicial e separação de responsabilidades.

**Critério de aceite proposto:** estrutura reproduzível, consistente com a arquitetura e verificável por revisão e build.

**Dependências:** baseline arquitetural e convenções de engenharia.

**Exclusões:** implementação de capacidades financeiras.

### I00-FEAT-002 — Python Toolchain & Quality

**Épico:** TS-EP-01  
**Pacote:** I00-02  
**Domínio principal proposto:** D07

**Objetivo:** estabelecer ambiente Python reproduzível e verificações automatizadas de qualidade.

**Escopo:** Python 3.12+, uv, Ruff, mypy, pytest e Hypothesis.

**Critério de aceite proposto:** instalação reproduzível, dependências fixadas e verificações executáveis.

**Dependências:** I00-FEAT-001.

**Exclusões:** treinamento de modelos de IA.

### I00-FEAT-003 — Versioned Contracts

**Épico:** TS-EP-01  
**Pacote:** I00-03  
**Domínio principal proposto:** D07, com participação de D05

**Objetivo:** estabelecer o catálogo inicial de contratos versionados.

**Escopo:** especificação, schemas, validação, compatibilidade e testes dos envelopes e registros iniciais.

**Critério de aceite proposto:** contratos versionados, válidos e testados.

**Dependências:** I00-FEAT-001 e I00-FEAT-002.

**Contratos iniciais:** CommandEnvelope.v1, EventEnvelope.v1, ErrorEnvelope.v1, HealthStatus.v1 e OutboxRecord.v1.

### I00-FEAT-004 — PostgreSQL & Migrations

**Épico:** TS-EP-02  
**Pacote:** I00-04  
**Domínio principal proposto:** D05

**Objetivo:** estabelecer persistência inicial e evolução controlada do schema.

**Escopo:** PostgreSQL 17, SQLAlchemy 2, Alembic, modelos iniciais e testes de migração.

**Critério de aceite proposto:** inicialização e migrations reproduzíveis, com integridade verificada.

**Dependências:** fundação do repositório, toolchain e infraestrutura local.

### I00-FEAT-005 — Transactional Outbox

**Épico:** TS-EP-02  
**Pacote:** I00-05  
**Domínio principal proposto:** D05

**Objetivo:** garantir persistência atômica entre estado de negócio e registro de evento aplicável.

**Escopo:** modelo Outbox, transações, estados de publicação, integridade e testes de rollback.

**Critério de aceite proposto:** atomicidade demonstrada em cenários de sucesso e falha.

**Dependências:** I00-FEAT-003 e I00-FEAT-004.

**Invariante:** uma alteração que exige evento não poderá ser confirmada sem seu registro Outbox na mesma transação.

### I00-FEAT-006 — Event Dispatcher

**Épico:** TS-EP-02  
**Pacote:** I00-06  
**Domínio principal proposto:** D05

**Objetivo:** processar e publicar eventos persistidos na Outbox.

**Escopo:** seleção de registros, publicação, tentativas, recuperação, concorrência e telemetria.

**Critério de aceite proposto:** publicação recuperável, sem perda silenciosa de eventos.

**Dependências:** I00-FEAT-003, I00-FEAT-004 e I00-FEAT-005.

**Semântica proposta:** at-least-once, sujeita à especificação detalhada.

### I00-FEAT-007 — Idempotent Consumers

**Épico:** TS-EP-02  
**Pacote:** I00-07  
**Domínio principal proposto:** D05

**Objetivo:** evitar duplicação indevida de efeitos sob entregas repetidas.

**Escopo:** identidade de mensagens, deduplicação, consistência do efeito, ordenação aplicável e recuperação.

**Critério de aceite proposto:** testes demonstram que a repetição não duplica efeitos confirmados.

**Dependências:** I00-FEAT-003, I00-FEAT-004 e I00-FEAT-006.

### I00-FEAT-008 — Foundation API

**Épico:** TS-EP-01  
**Pacote:** I00-08  
**Domínio principal proposto:** D07

**Objetivo:** disponibilizar interfaces técnicas básicas da fundação.

**Escopo:** FastAPI, Pydantic v2, health checks, validação e respostas de erro.

**Critério de aceite proposto:** interfaces verificadas por testes de contrato e integração.

**Dependências:** I00-FEAT-002 e I00-FEAT-003.

**Exclusões:** endpoints para execução financeira.

### I00-FEAT-009 — Security & Environment Isolation

**Épico:** TS-EP-01  
**Pacote:** I00-09  
**Domínio principal proposto:** D06

**Objetivo:** estabelecer controles iniciais de segurança e segregação.

**Escopo:** configuração por ambiente, proteção de segredos, permissões, bloqueios e isolamento TRAINING/PAPER/LIVE.

**Critério de aceite proposto:** testes demonstram segregação e impossibilidade de acessar LIVE no I00.

**Dependências:** configuração da fundação e interfaces relevantes.

**Invariante:** ausência de credenciais e execução financeira LIVE.

### I00-FEAT-010 — Observability Foundation

**Épico:** TS-EP-01  
**Pacote:** I00-10  
**Domínio principal proposto:** D06

**Objetivo:** estabelecer observabilidade técnica compartilhada.

**Escopo:** logs JSON, métricas, traces, correlação, health e diagnóstico.

**Critério de aceite proposto:** eventos relevantes de execução, erro e recuperação são observáveis e correlacionáveis.

**Dependências:** estrutura da fundação e contratos de telemetria aplicáveis.

### I00-FEAT-011 — CI/CD Foundation

**Épico:** TS-EP-01  
**Pacote:** I00-11  
**Domínio principal proposto:** D06

**Objetivo:** automatizar verificações de qualidade e identificação de builds.

**Escopo:** GitHub Actions, instalação, lint, tipagem, testes, validação de contratos e relatórios.

**Critério de aceite proposto:** pipeline reproduzível com bloqueio diante de verificações obrigatórias não atendidas.

**Dependências:** I00-FEAT-001 e I00-FEAT-002.

**Exclusões:** deployment LIVE.

### I00-FEAT-012 — Documentation & Traceability

**Épico:** TS-EP-01  
**Pacote:** I00-12  
**Domínio principal proposto:** D07

**Objetivo:** manter documentação e rastreabilidade técnica.

**Escopo:** Document Registry, Gap Register, Traceability Matrix, Approval Register, Change Log e especificações.

**Critério de aceite proposto:** artefatos obrigatórios identificados, relações verificáveis e lacunas explicitadas.

**Dependências:** baselines e registros de governança aprovados.

**Limite:** não declarar documentação completa enquanto existirem vínculos obrigatórios pendentes.

### I00-FEAT-013 — Failure & Recovery Validation

**Épico:** TS-EP-02  
**Pacote:** I00-13  
**Domínio principal proposto:** D07, com participação de D05 e D06

**Objetivo:** verificar falhas e recuperação dos mecanismos de fundação.

**Escopo:** testes de transação, Dispatcher, duplicidade, reinício, concorrência e recuperação.

**Critério de aceite proposto:** cenários adversos demonstram preservação dos invariantes aplicáveis.

**Dependências:** I00-FEAT-004–007, com infraestrutura de testes.

**Limite:** testes realizados somente em ambientes controlados.

### I00-FEAT-014 — Evidence & G0 Preparation

**Épico:** TS-EP-01  
**Pacote:** I00-14  
**Domínio principal proposto:** D07

**Objetivo:** preparar o pacote de evidências para avaliação do I00 e do gate G0.

**Escopo:** inventário de critérios, manifestos, resultados, integridade, rastreabilidade e checklist G0.

**Critério de aceite proposto:** Evidence Bundle completo e validável, com cobertura dos critérios aplicáveis.

**Dependências:** resultados das Features e testes correspondentes.

**Limite:** preparar evidências não equivale a homologar G0.

---

## 6. Matriz de dependências

As dependências abaixo constituem uma proposta inicial de planejamento.

| Feature | Dependências principais |
|---|---|
| FEAT-001 | Baseline arquitetural |
| FEAT-002 | FEAT-001 |
| FEAT-003 | FEAT-001, FEAT-002 |
| FEAT-004 | FEAT-001, FEAT-002 |
| FEAT-005 | FEAT-003, FEAT-004 |
| FEAT-006 | FEAT-003, FEAT-004, FEAT-005 |
| FEAT-007 | FEAT-003, FEAT-004, FEAT-006 |
| FEAT-008 | FEAT-002, FEAT-003 |
| FEAT-009 | Configuração e interfaces aplicáveis |
| FEAT-010 | Fundação e componentes instrumentáveis |
| FEAT-011 | FEAT-001, FEAT-002 |
| FEAT-012 | Baselines e registros de governança |
| FEAT-013 | FEAT-004–007 e infraestrutura de testes |
| FEAT-014 | Critérios, testes e evidências das Features |

Os prefixos FEAT-001–014 nesta tabela referem-se a I00-FEAT-001–014.

Essas dependências deverão ser refinadas e validadas nas especificações individuais.

## 7. Histórias técnicas

O backlog inicial aprovado contém TS-ST-001–024.

Associações formalizadas pelo usuário em 17/11/2026:

| Story ID | Feature relacionada | Estado |
|---|---|---|
| TS-ST-001 | I00-FEAT-001 principal; I00-02 apoia toolchain e qualidade; I00-11 apoia CI e build. | APPROVED |
| TS-ST-002 | I00-FEAT-003 principal. | APPROVED |
| TS-ST-003 | I00-FEAT-005 principal; I00-FEAT-004 como dependência de PostgreSQL e migrações. | APPROVED |
| TS-ST-004 | I00-FEAT-006 principal; I00-FEAT-007 vinculada ao escopo obrigatório de deduplicação do consumidor e ao aceite da história. | APPROVED |

Uma história poderá contribuir para mais de uma Feature, desde que a responsabilidade principal e os critérios de aceite sejam explicitados.

Os vínculos deverão ser confirmados contra as descrições originais das histórias.

Nenhum novo Story ID será criado neste catálogo.

## 8. Rastreabilidade arquitetural

A matriz deverá relacionar:

**ADR → Componente → Pendência → Épico → Feature → História → Contrato → Teste → Evidência**

### 8.1 ADRs

As ADRs técnicas TS-ADR-089–098 deverão ser associadas às Features aplicáveis após verificação dos registros individuais.

### 8.2 Componentes

Os IDs específicos dos componentes deverão ser confirmados no catálogo original dos 33 componentes.

### 8.3 Pendências

As pendências P01–P106 deverão ser associadas somente quando sua descrição original e sua aplicabilidade forem verificadas.

### 8.4 Estado inicial

**Traceability Status:** INCOMPLETE.

Nenhum vínculo individual ainda não confirmado poderá ser marcado VERIFIED.

## 9. Critérios de aceite do catálogo

O catálogo poderá ser aprovado quando:

1. As 14 Features estiverem identificadas.
2. Cada Feature possuir objetivo e escopo.
3. Cada Feature possuir épico principal.
4. Os pacotes I00-01–14 estiverem contemplados.
5. As fronteiras TS-EP-01 / TS-EP-02 estiverem explícitas.
6. As dependências iniciais estiverem registradas.
7. Os critérios de aceite propostos estiverem definidos.
8. Os vínculos de histórias estiverem identificados como propostos ou verificados.
9. As lacunas documentais estiverem preservadas.
10. As restrições de segurança e LIVE estiverem preservadas.

A aprovação do catálogo não comprovará a satisfação dos critérios de implementação das Features.

## 10. Documentation Readiness

### 10.1 Condições

Para iniciar a implementação de uma Feature, deverão estar disponíveis:

- Especificação individual aprovada.
- Requisitos verificáveis.
- ADRs aplicáveis identificadas.
- Componentes responsáveis definidos.
- Histórias selecionadas READY.
- Contratos necessários especificados.
- Dependências bloqueantes resolvidas.
- Testes e critérios de aceite definidos.
- Restrições de segurança documentadas.

### 10.2 Estado inicial

**Feature Catalog:** IN_REVIEW.

**Feature Documentation Readiness:** NOT_READY.

A aprovação do catálogo não promoverá automaticamente nenhuma Feature a READY.

## 11. Lacunas documentais

| Gap ID | Impacto |
|---|---|
| DOC-GAP-001 | Reconciliação P01–P47 |
| DOC-GAP-002 | Classificação provisória P18 |
| DOC-GAP-003 | Integralidade ADR-001–088 |
| DOC-GAP-004 | Formalização TS-ADR-089–098 |
| DOC-GAP-005 | Rastreabilidade integral |
| DOC-GAP-006 | Refinamento de Features e histórias |
| DOC-GAP-007 | Verificação dos arquivos |
| DOC-GAP-008 | Owners e aprovações |

A aprovação deste catálogo poderá resolver parte da necessidade de identificação de Features em DOC-GAP-006, mas não encerrará automaticamente a lacuna.

## 12. Segurança e restrições

O catálogo deverá preservar:

- Segregação TRAINING/PAPER/LIVE.
- LIVE inacessível no I00.
- Ausência de credenciais LIVE.
- Ausência de envio de ordens reais.
- Proibição de bypass de Control → Risk → Execution.
- Idempotência e integridade transacional.
- Auditoria e rastreabilidade.
- Aprovação humana para alterações normativas.
- Evidências verificáveis antes de aceites.

Nenhuma Feature do I00 poderá habilitar execução financeira real.

## 13. Implementation Acceptance

O aceite individual de cada Feature deverá seguir sua especificação aprovada.

Uma Feature somente poderá ser considerada aceita quando:

- Histórias obrigatórias concluídas.
- Critérios de aceite atendidos.
- Testes executados.
- Contratos conformes.
- Evidências verificadas.
- Lacunas bloqueantes resolvidas.
- Rastreabilidade atualizada.
- Aprovação competente registrada.

**Implementation Acceptance de todas as Features:** NOT_EVALUATED.

O aceite das Features não homologará automaticamente o I00 ou G0.

## 14. Sequência de refinamento

Após aprovação deste catálogo, o refinamento documental deverá prosseguir individualmente, começando por:

**I00-FEAT-001 — Monorepo Bootstrap.**

As demais Features deverão seguir a sequência aprovada ou uma alteração formalmente autorizada.

Não será iniciada implementação de software nesta etapa documental.

## 15. Histórico de alterações

| Version | Date | Change ID | Description | Approval |
|---|---|---|---|---|
| 1.0.0-draft.1 | 2026-11-16 | PENDING | Catálogo inicial das 14 Features I00 | PENDING |
| 1.0 | 2026-11-16 | N/A | Aprovação documental do catálogo sem alteração de escopo | [16/11/2026 · aprovação sem ressalvas](../governance/history/TS-I00-FEAT-CAT-001/APPROVAL.md) |

## 16. Registro de aprovação

| Campo | Valor |
|---|---|
| Artifact ID | TS-I00-FEAT-CAT-001 |
| Version | 1.0 |
| Approval Category | DOC |
| Decision | APPROVED · catálogo documental |
| Approved By | Usuário no chat de governança |
| Approval Reference | [16/11/2026 · aprovação sem ressalvas](../governance/history/TS-I00-FEAT-CAT-001/APPROVAL.md) |
| Conditions | Sem ressalvas |
| Date | 2026-11-16 |

---

**Document Status:** APPROVED  
**Feature Count:** 14 — PROPOSED  
**Documentation Readiness:** NOT_READY  
**Implementation Acceptance:** NOT_EVALUATED  
**Gate G0:** NOT_EVALUATED  
**LIVE Authorization:** NOT_AUTHORIZED

**Next Artifact:** I00-FEAT-001.md

**Próxima etapa:** aguardar o conteúdo do I00-FEAT-001.md.

## 17. Histórico da revisão e estado do I00

O [anexo original](../governance/history/TS-I00-FEAT-CAT-001/IN-REVIEW.txt) está arquivado. A versão documental **1.0** foi aprovada em 16/11/2026. O histórico preserva a [revisão local anterior à aprovação](../governance/history/TS-I00-FEAT-CAT-001/REVISAO-LOCAL-IN-REVIEW.txt). As Features, os vínculos e os estados de prontidão mantêm o escopo e a classificação do texto submetido.

O [aceite do Evidence Bundle RC1](../governance/DOC-07-RC1-ACCEPTANCE.md) conserva o recorte de I00-14 e AC12. O [dossiê de G0](../governance/G0-REVIEW-DOSSIER.md) registra AC02, AC07 e AC09 em aberto. G0 segue em revisão e LIVE permanece indisponível.


### Decisão de vínculos de histórias — 17/11/2026

O usuário aprovou nesta conversa os vínculos de escopo das histórias TS-ST-001–004 conforme o catálogo de Features. Registro aplicado às referências correspondentes neste documento.