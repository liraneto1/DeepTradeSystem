# GAP-REGISTER.md
## TRADE SYSTEM V1 — Documentation Gap Register

**Document ID:** TS-DOC-GAP-001  
**Version:** 1.0  
**Status:** APPROVED  
**Domain:** GLOBAL / D07  
**Increment:** I00–I09  
**Owner:** Architecture & Documentation Governance  
**Governing Standard:** TS-DOC-STD-V1.0 — APPROVED  
**Document Registry:** TS-DOC-REG-001 — APPROVED  
**Architecture Baseline:** TS-ARCH-GLOBAL-V1.0 — APPROVED  
**Engineering Baseline:** TS-ENG-I00-V1.0 — APPROVED  
**Approval Reference:** [16/11/2026 · GAP-R01–GAP-R10 aprovadas sem ressalvas](history/TS-DOC-GAP-001/APPROVAL.md)  
**Source References:** [TS-DOC-STD-V1.0](TS-DOC-STD-V1.0.md), [Document Registry](DOCUMENT-REGISTRY.md), [texto submetido](history/TS-DOC-GAP-001/IN-REVIEW.txt) e [auditoria documental](AUDITORIA-DOCUMENTAL-I00.md)  
**Related ADRs:** ADR-001–088 e TS-ADR-089–098, conforme DOC-GAP-003 e DOC-GAP-004  
**Related Components:** consultar [matriz de rastreabilidade](REQUIREMENTS-TRACEABILITY-MATRIX.md) e vínculos por lacuna. Componentes sem vínculo demonstrado permanecem TBD.  
**Related Requirements/Pendências:** P01–P47, P18 e critérios I00-AC02, I00-AC07, I00-AC09 e I00-AC12 no contexto de G0  
**Dependencies:** Document Registry, reconciliações de pendências e ADRs, Traceability Matrix e dossiê de G0  
**Acceptance Criteria:** seção 12  
**Last Updated:** 2026-11-16

---

## 1. Objetivo

Estabelecer o processo de identificação, classificação, priorização, tratamento, validação e encerramento das lacunas documentais do TRADE SYSTEM V1.

O registro deverá assegurar que:

- Requisitos tenham fontes identificáveis.
- Decisões aprovadas estejam preservadas.
- Documentos obrigatórios estejam disponíveis antes da implementação correspondente.
- Inconsistências sejam tratadas antes de impactar código, contratos ou testes.
- Lacunas críticas bloqueiem as atividades afetadas.
- O histórico de resolução seja auditável.

## 2. Definição de lacuna documental

Uma lacuna documental representa ausência, incompletude, inconsistência, ambiguidade ou falta de evidência de aprovação de uma informação necessária ao projeto.

As lacunas poderão ser classificadas como:

| Tipo | Descrição |
|---|---|
| MISSING_DOCUMENT | Documento obrigatório inexistente ou não localizado |
| INCOMPLETE_DOCUMENT | Documento existente com informações obrigatórias ausentes |
| MISSING_REQUIREMENT | Requisito necessário ainda não especificado |
| TRACEABILITY_GAP | Ausência de vínculo entre artefatos |
| INCONSISTENCY | Informações conflitantes entre documentos |
| APPROVAL_GAP | Aprovação ausente ou não verificável |
| VERSION_MISMATCH | Divergência entre versões |
| MISSING_EVIDENCE | Evidência obrigatória não produzida ou não localizada |
| OWNERSHIP_GAP | Responsabilidade não definida |
| SOURCE_UNVERIFIED | Conteúdo cuja origem ou integridade não foi confirmada |

A ausência de evidência futura, ainda não exigível pelo estágio do projeto, deverá ser registrada como pendência planejada, não necessariamente como defeito.

## 3. Modelo de registro

Cada lacuna deverá possuir:

| Campo | Descrição |
|---|---|
| Gap ID | Identificador único |
| Title | Nome resumido |
| Description | Descrição objetiva |
| Gap Type | Categoria da lacuna |
| Source Reference | Fonte que sustenta a identificação |
| Affected Documents | Documentos afetados |
| Affected ADRs | Decisões relacionadas |
| Affected Components | Componentes relacionados |
| Affected Increment | Incrementos impactados |
| Severity | Criticidade |
| Blocking Scope | Atividades impedidas |
| Functional Owner | Responsável funcional |
| Resolution Action | Ação necessária |
| Status | Estado de tratamento |
| Resolution Evidence | Evidência de resolução |
| Approval Reference | Aprovação do encerramento |
| Created At | Data de identificação |
| Updated At | Última atualização |

Campos não conhecidos deverão permanecer explicitamente como `TBD`, sem preenchimento presumido.

## 4. Classificação de criticidade

| Severidade | Critério | Tratamento |
|---|---|---|
| CRITICAL | Pode comprometer segurança financeira, autorização, integridade ou segregação de ambientes | Bloqueia atividades afetadas imediatamente |
| HIGH | Impede implementação correta ou verificação de requisito essencial | Resolver antes do início da atividade dependente |
| MEDIUM | Compromete rastreabilidade, clareza ou manutenção, sem impedir necessariamente o trabalho independente | Planejar resolução antes do aceite aplicável |
| LOW | Melhoria documental sem impacto relevante imediato | Resolver conforme priorização |

A severidade deverá ser acompanhada de justificativa.

A classificação de criticidade não substitui a análise de dependências. Uma lacuna HIGH em um componente futuro não bloqueia automaticamente o bootstrap independente do I00.

## 5. Estados de tratamento

| Estado | Significado |
|---|---|
| IDENTIFIED | Lacuna identificada |
| TRIAGED | Impacto, criticidade e owner avaliados |
| IN_PROGRESS | Resolução em andamento |
| IN_REVIEW | Correção aguardando validação |
| RESOLVED | Resolução aprovada e evidenciada |
| ACCEPTED_RISK | Exceção formalmente aceita pela autoridade competente |
| DEFERRED | Tratamento postergado com justificativa e prazo ou condição de revisão |
| REOPENED | Lacuna reaberta após nova evidência |

Uma lacuna não poderá ser considerada `RESOLVED` apenas porque um documento foi criado. Será necessário demonstrar que a informação ausente foi corrigida e validada.

## 6. Registro inicial de lacunas conhecidas

Os registros abaixo derivam das limitações documentais já reconhecidas no processo de consolidação. Sua criticidade e seu escopo de bloqueio são propostas iniciais, sujeitas a triagem.

### DOC-GAP-001 — Reconciliação P01–P47

**Tipo:** SOURCE_UNVERIFIED / TRACEABILITY_GAP  
**Severidade proposta:** HIGH  
**Domínios:** D01–D04  
**Incrementos:** I00–I09, conforme dependência  
**Owner funcional:** Architecture & Documentation Governance  
**Estado:** IDENTIFIED

**Descrição:** As descrições originais das pendências P01–P47 não foram integralmente confirmadas nos documentos consolidados.

**Ação:** recuperar os registros originais, conferir identificadores, descrições, classificação, dependências e vínculos.

**Bloqueio:** impede declarar rastreabilidade integral dessas pendências; poderá bloquear histórias que dependam de conteúdo ainda não confirmado.

**Evidência de resolução:** registro mestre reconciliado, referências às fontes originais e revisão aprovada.

### DOC-GAP-002 — Classificação de P18

**Tipo:** INCOMPLETE_DOCUMENT  
**Severidade proposta:** MEDIUM  
**Domínio:** D02  
**Incremento:** fase M3 provisória; impacto em incrementos a confirmar  
**Owner funcional:** Architecture / AI  
**Estado:** IDENTIFIED

**Descrição:** A classificação de P18 como M3 permanece provisória.

**Ação:** confirmar descrição original, escopo, dependências e fase de entrega.

**Bloqueio:** impede considerar definitiva a classificação de P18, mas não bloqueia atividades independentes do I00.

**Evidência de resolução:** decisão de classificação aprovada e registro mestre atualizado.

### DOC-GAP-003 — Integralidade das ADR-001–088

**Tipo:** SOURCE_UNVERIFIED  
**Severidade proposta:** HIGH  
**Domínios:** D01–D07  
**Incrementos:** I00–I09  
**Owner funcional:** Architecture Governance  
**Estado:** IDENTIFIED

**Descrição:** As 88 ADRs possuem aprovação arquitetural registrada, mas seus textos individuais completos ainda precisam ser verificados contra as fontes originais.

**Ação:** localizar, conferir e catalogar cada ADR, incluindo contexto, decisão, consequências e referências.

**Bloqueio:** impede atestar completude documental integral; ADRs não verificadas deverão ser analisadas antes de implementar funcionalidades que dependam de seus detalhes.

**Evidência de resolução:** inventário ADR-001–088 com localização, versão, integridade e fonte verificadas.

### DOC-GAP-004 — Formalização das TS-ADR-089–098

**Tipo:** INCOMPLETE_DOCUMENT  
**Severidade proposta:** HIGH  
**Domínio:** GLOBAL / D06 / D07  
**Incremento:** I00  
**Owner funcional:** Engineering Architecture  
**Estado:** IDENTIFIED

**Descrição:** As decisões técnicas foram aprovadas, mas seus registros individuais completos precisam ser materializados e verificados.

**Ação:** produzir os registros das dez ADRs, preservando rigorosamente as decisões aprovadas.

**Bloqueio:** impede declarar completa a documentação das ADRs técnicas. Não exige reaprovar as decisões já validadas, salvo alteração material.

**Evidência de resolução:** dez registros versionados e conferidos com a aprovação original.

### DOC-GAP-005 — Matriz integral de rastreabilidade

**Tipo:** TRACEABILITY_GAP  
**Severidade proposta:** HIGH  
**Domínios:** D01–D07  
**Incrementos:** I00–I09  
**Owner funcional:** Documentation Governance  
**Estado:** IDENTIFIED

**Descrição:** A cadeia ADR → Componente → Pendência → Épico → Feature → História → Contrato → Teste → Evidência ainda não está integralmente preenchida.

**Ação:** construir e validar os vínculos, distinguindo relacionamentos existentes, planejados, não aplicáveis e não verificados.

**Bloqueio:** impede declarar rastreabilidade integral; cada história deverá possuir vínculos suficientes antes de ser considerada READY.

**Evidência de resolução:** matriz validada, com referências verificáveis e exceções justificadas.

### DOC-GAP-006 — Features e histórias técnicas do I00

**Tipo:** INCOMPLETE_DOCUMENT  
**Severidade proposta:** HIGH  
**Domínio:** D07 / GLOBAL  
**Incremento:** I00  
**Owner funcional:** Engineering / QA  
**Estado:** IDENTIFIED

**Descrição:** Os 14 pacotes de trabalho do I00 foram aprovados, mas a decomposição formal em Features e o refinamento completo das histórias permanecem pendentes.

**Ação:** definir Features, mapear histórias existentes, criar novas histórias somente quando necessário e especificar critérios de aceite.

**Bloqueio:** histórias insuficientemente especificadas não poderão entrar em desenvolvimento.

**Evidência de resolução:** catálogo de Features e histórias com Documentation Readiness validado.

### DOC-GAP-007 — Verificação física dos documentos

**Tipo:** SOURCE_UNVERIFIED / VERSION_MISMATCH  
**Severidade proposta:** HIGH  
**Domínios:** GLOBAL / D01–D07  
**Incrementos:** I00–I09  
**Owner funcional:** Documentation Governance  
**Estado:** IDENTIFIED

**Descrição:** A correspondência entre documentos aprovados nesta conversa e arquivos efetivamente presentes no repositório ainda não foi auditada.

**Ação:** verificar caminhos, versões, integridade, conteúdo e referências de aprovação.

**Bloqueio:** documentos não verificados não poderão ser tratados como fontes autoritativas de implementação sem conferência.

**Evidência de resolução:** relatório de auditoria do repositório e Document Registry atualizado.

### DOC-GAP-008 — Owners e referências de aprovação

**Tipo:** OWNERSHIP_GAP / APPROVAL_GAP  
**Severidade proposta:** MEDIUM  
**Domínios:** GLOBAL / D01–D07  
**Incrementos:** I00–I09  
**Owner funcional:** Project Governance  
**Estado:** IDENTIFIED

**Descrição:** Os owners funcionais estão identificados, mas responsáveis nominais e referências formais de algumas aprovações ainda precisam ser associados aos artefatos.

**Ação:** definir matriz de responsabilidades e registrar referências de aprovação.

**Bloqueio:** impede aceite formal de entregas que exijam responsáveis ou alçadas ainda não definidos.

**Evidência de resolução:** matriz de responsabilidades e Approval Register atualizados.

## 7. Matriz de priorização inicial

| Gap | Severidade proposta | Prioridade de tratamento | Impacto no I00 |
|---|---|---|---|
| DOC-GAP-001 | HIGH | Antes das histórias dependentes | Condicional |
| DOC-GAP-002 | MEDIUM | Antes da classificação definitiva de P18 | Não bloqueante para bootstrap |
| DOC-GAP-003 | HIGH | Antes de implementar decisões não verificadas | Condicional |
| DOC-GAP-004 | HIGH | Durante preparação documental I00 | Relevante |
| DOC-GAP-005 | HIGH | Antes do READY das histórias | Relevante |
| DOC-GAP-006 | HIGH | Antes da implementação das histórias afetadas | Bloqueante por história |
| DOC-GAP-007 | HIGH | Antes de confiar nos arquivos como fonte normativa | Relevante |
| DOC-GAP-008 | MEDIUM | Antes dos aceites formais aplicáveis | Condicional |

A priorização definitiva deverá considerar dependências, criticidade e escopo da atividade.

## 8. Processo de resolução

1. **Identificar:** registrar a lacuna e sua fonte.
2. **Triar:** determinar impacto, criticidade, owner e bloqueios.
3. **Planejar:** definir ação e critério de resolução.
4. **Corrigir:** produzir ou atualizar os artefatos necessários.
5. **Verificar:** comparar a correção com as fontes autoritativas.
6. **Revisar:** submeter à autoridade responsável.
7. **Encerrar:** registrar evidências e aprovação.
8. **Atualizar:** sincronizar Document Registry e Traceability Matrix.

Nenhuma lacuna poderá ser encerrada exclusivamente por declaração automática do TS-DOC-GOV.

## 9. Critérios de bloqueio

Uma lacuna deverá bloquear a atividade afetada quando:

- O requisito essencial não possuir origem confiável.
- Houver conflito não resolvido entre decisões normativas.
- Um contrato crítico estiver ausente ou ambíguo.
- Uma autorização financeira ou regra de risco estiver indefinida.
- Uma história não atender à Definition of Ready.
- A implementação depender de uma ADR cujo conteúdo necessário não esteja confirmado.
- Uma evidência obrigatória para aceite estiver ausente.
- A segurança ou segregação de ambientes não puder ser demonstrada.

A resolução de uma lacuna não autoriza automaticamente a implementação. Os critérios de prontidão e as aprovações aplicáveis continuam obrigatórios.

## 10. Política de exceções

Lacunas não críticas poderão ser postergadas mediante:

- Justificativa documentada.
- Avaliação de impacto.
- Owner responsável.
- Condição de reavaliação.
- Aprovação da autoridade competente.
- Registro no Gap Register.

Lacunas que comprometam invariantes financeiros, integridade, autorização ou segregação de ambientes não poderão ser dispensadas para permitir operação insegura.

A aceitação de uma lacuna documental não substitui os gates G0–G5.

## 11. Indicadores de governança documental

O TS-DOC-GOV deverá acompanhar:

- Total de lacunas abertas.
- Lacunas por domínio.
- Lacunas por incremento.
- Lacunas por severidade.
- Lacunas bloqueantes.
- Tempo de resolução.
- Documentos com fontes não verificadas.
- Histórias impedidas de atingir READY.
- Percentual de rastreabilidade verificada.
- Lacunas reabertas.

Os indicadores deverão ser calculados a partir dos registros reais, sem estimativas apresentadas como resultados observados.

## 12. Critérios de aceite deste documento

O GAP-REGISTER.md estará apto à aprovação quando:

1. Os tipos de lacunas estiverem definidos.
2. O modelo de registro estiver completo.
3. As severidades estiverem padronizadas.
4. Os estados de tratamento estiverem definidos.
5. As oito lacunas iniciais estiverem identificadas.
6. Os impactos e bloqueios estiverem diferenciados.
7. O processo de resolução estiver estabelecido.
8. A política de exceções estiver definida.
9. Os indicadores de governança estiverem especificados.
10. A segurança e os gates G0–G5 estiverem preservados.

---

**Status:** APPROVED  
**Approval Reference:** [16/11/2026 · GAP-R01–GAP-R10 aprovadas sem ressalvas](history/TS-DOC-GAP-001/APPROVAL.md)  
**Próximo documento:** TRACEABILITY-MATRIX.md  
**Próxima etapa:** aguardar instrução para revisar a Traceability Matrix.

## 13. Histórico e andamento registrado

O [texto submetido](history/TS-DOC-GAP-001/IN-REVIEW.txt), a [edição local anterior](history/TS-DOC-GAP-001/EDICAO-LOCAL-ANTERIOR.txt) e o [bloco de aprovação recebido](history/TS-DOC-GAP-001/TEXTO-DE-APROVACAO-RECEBIDO.md) estão arquivados. A versão **1.0** foi aprovada em 16/11/2026. O histórico também preserva a [revisão local antes da aprovação](history/TS-DOC-GAP-001/REVISAO-LOCAL-IN-REVIEW.txt).

DOC-GAP-001–008 permanecem abertas. Os estados iniciais da seção 6 foram preservados. A [reconciliação de P01–P106](PENDING-ITEM-RECONCILIATION.md) e a [reconciliação de ADRs](ADR-RECONCILIATION.md) registram avanços para DOC-GAP-001, DOC-GAP-003 e DOC-GAP-004. O [Document Registry aprovado](DOCUMENT-REGISTRY.md) distingue a localização dos arquivos da conferência integral de versão e conteúdo para DOC-GAP-007. P18 segue M3 provisório. [Ressalvas de reconciliação](RECONCILIATION-DECISIONS.md)

Os blocos abaixo preservam o acompanhamento de I00/G0 e as lacunas complementares da edição local anterior. A aprovação já registrada da classificação dos bloqueios de G0 mantém seu escopo.

## Bloqueios para submeter G0 a aceite

O usuário aprovou a classificação destes itens como bloqueantes em 16/11/2026. O fechamento de cada item segue pendente. [Decisão](APPROVAL-REGISTER.md) · [Validações de Engenharia](G0-REVIEW-DOSSIER.md#validações-pendentes-de-engenharia-para-g0)

| Referência | Situação comprovada | O que falta e quem atua |
|---|---|---|
| DOC-06 · I00-AC02 | Repetição PostgreSQL por digest passou em 38 testes para d561026. Triagem da imagem e inventário estático Linux parciais. | Engenharia completa disposição dos achados da imagem, prova seleção e carregamento de componentes nativos no runner e captura versões efetivas, resolução de build isolado, avisos, hashes e logs de wheel/sdist. QA confere identidade e Segurança decide correções ou exceções. [Retorno](../evidence/AC02-d561026-retorno-engenharia.md) |
| DOC-04 · I00-AC07 | Política aprovada. O candidato local 184e8b3 tem 153 testes em PostgreSQL 17.11 e inclui a correção de event_id divergente. Pré-checagem de legados validada com fixture. | Engenharia e donos dos produtores confirmam cardinalidade e fonte autoritativa. Administração do banco e QA identificam snapshot autorizado anterior à migração 0016, executam a pré-checagem somente leitura e registram eventual reconciliação. Revisar controles de operação e parâmetros testados da política. Engenharia e QA emitem parecer e submetem ao aceite humano. [Dossiê](G0-REVIEW-DOSSIER.md) · [Parâmetros](../evidence/AC07-parametros-operacionais.md) |
| DOC-05 · I00-AC09 | Definições aprovadas. Coletor validado em integração com 146 testes registrados no snapshot do ensaio. | Engenharia e QA vinculam ou repetem o ensaio no candidato submetido, demonstram a duração desde a detecção do bloqueio e apresentam frequência, janela, limiares, retenção, tratamento de timestamps e responsáveis para decisão. [DOC-05](DOC-05-OUTBOX-METRICS.md) · [Evidência](../evidence/AC09-coletor-outbox.md) |
| G0 · DOC-07 · AC12 | I00-14 e bundle RC1 aceitos no recorte original, com oito hashes conferidos na recuperação. | Identificar o candidato submetido a G0 e consolidar evidências e ressalvas de I00–I04 no escopo da decisão. Explicitar o que pode ser reutilizado por versão/ambiente e o que exige repetição. Registrar a decisão humana em ata. [DOC-07](DOC-07-RC1-ACCEPTANCE.md) · [Dossiê](G0-REVIEW-DOSSIER.md) |

## Lacunas de documentação e fontes para revisão

| Referência | Lacuna preservada | Encaminhamento |
|---|---|---|
| Contratos de I00 | OpenAPI em runtime e propostas ErrorEnvelope.v1, HealthStatus.v1 e OutboxRecord.v1. A obrigação de publicar cada artefato individual depende de decisão. | Confirmar o recorte do catálogo mínimo já aprovado e apontar a decisão por artefato se aplicável. [Contratos](../03-CONTRATOS.md) |
| TS-ADR-089–098 | Decisões aprovadas, com resumos e fonte original. Campos de fichas individuais ainda exigem conferência por ID. | Fornecer registros específicos quando disponíveis ou autorizar fichas retrospectivas com indicação explícita dos campos sem fonte. [Reconciliação](ADR-RECONCILIATION.md) |
| DOC-01–03 | Reconciliação de IDs disponível. Permanecem vínculos sem fonte e responsáveis nominais. P18 segue M3 provisório. | Decidir P18 separadamente e indicar fontes/owners para os vínculos identificados. [Ressalvas](RECONCILIATION-DECISIONS.md) · [DOC-03](DOC-03-CONSOLIDATION.md) |
| Demais lacunas históricas | A recuperação trouxe novas fontes e resultados após a primeira auditoria. | Consultar o [levantamento histórico](DOCUMENT-GAP-ANALYSIS.md) e a [recuperação](SOURCE-RECOVERY.md). Confirmar impacto antes de classificar uma lacuna documental como bloqueio de G0. |

LIVE permanece indisponível.
