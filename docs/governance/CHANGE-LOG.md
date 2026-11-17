# CHANGE-LOG.md
## TRADE SYSTEM V1 — Master Change Log & Change Control

**Document ID:** TS-DOC-CHG-001  
**Version:** 1.0  
**Status:** APPROVED  
**Domain:** GLOBAL / D07  
**Increment:** I00–I09  
**Owner:** Architecture & Documentation Governance  
**Governing Standard:** TS-DOC-STD-V1.0 — APPROVED  
**Document Registry:** TS-DOC-REG-001 — APPROVED  
**Gap Register:** TS-DOC-GAP-001 — APPROVED  
**Traceability Matrix:** TS-DOC-TRC-001 — APPROVED  
**Approval Register:** TS-DOC-APR-001 — APPROVED  
**Architecture Baseline:** TS-ARCH-GLOBAL-V1.0 — APPROVED  
**Engineering Baseline:** TS-ENG-I00-V1.0 — APPROVED  
**Approval Reference:** [16/11/2026 · CHG-R01–CHG-R10 aprovadas sem ressalvas](history/TS-DOC-CHG-001/APPROVAL.md)  
**Source References:** [texto submetido](history/TS-DOC-CHG-001/IN-REVIEW.txt), [TS-DOC-STD-V1.0](TS-DOC-STD-V1.0.md) e [originais TXT](../referencias/originais/)  
**Related ADRs:** N/A para a revisão do modelo. Registrar as ADRs afetadas por mudança, conforme seção 6.  
**Related Components:** N/A para a revisão do modelo. Identificar por mudança, conforme seções 6 e 12.  
**Related Requirements/Pendências:** DOC-GAP-001–008, conforme seção 11  
**Dependencies:** [Document Registry](DOCUMENT-REGISTRY.md), [Gap Register](GAP-REGISTER.md), [Traceability Matrix](TRACEABILITY-MATRIX.md) e [Approval Register](APPROVAL-REGISTER.md)  
**Acceptance Criteria:** seção 16  
**Last Updated:** 2026-11-16

---

## 1. Objetivo

Estabelecer o registro mestre de mudanças do TRADE SYSTEM V1, assegurando que alterações em documentos, decisões, requisitos, contratos, implementações e evidências sejam identificadas, avaliadas, aprovadas e rastreadas.

O Change Log deverá permitir reconstruir:

- O estado anterior de um artefato.
- A alteração realizada ou proposta.
- A justificativa da mudança.
- O impacto técnico, funcional e operacional.
- Os documentos e componentes afetados.
- A autoridade que aprovou a mudança.
- Os testes e evidências necessários à revalidação.
- A versão resultante.

## 2. Princípios de controle de mudanças

1. **Change Traceability:** toda alteração material deverá possuir registro.
2. **Baseline Integrity:** baselines aprovadas não poderão ser modificadas silenciosamente.
3. **Impact Before Approval:** mudanças materiais exigem análise de impacto antes da aprovação.
4. **Version-Specific Changes:** cada alteração deverá identificar versões de origem e destino.
5. **Immutable History:** registros anteriores deverão permanecer auditáveis.
6. **Evidence Revalidation:** evidências impactadas deverão ser reavaliadas.
7. **Human Approval:** alterações normativas exigem aprovação humana competente.
8. **Controlled Evolution:** mudanças deverão preservar compatibilidade e segurança ou formalizar suas consequências.
9. **No Implicit LIVE Authorization:** mudanças técnicas ou documentais não autorizam LIVE.
10. **Single Source of Truth:** a alteração deverá atualizar os registros autoritativos, evitando documentos divergentes.

## 3. Escopo de aplicação

O controle de mudanças abrangerá:

- Architecture Baselines.
- Engineering Baselines.
- ADRs.
- Componentes.
- Requisitos e pendências.
- Incrementos e roadmap.
- Épicos, Features e histórias técnicas.
- Contratos e schemas.
- Modelos de dados.
- Políticas de risco.
- Modelos de IA e datasets.
- Testes e critérios de aceite.
- Evidências e homologações.
- Configurações operacionais.
- Documentação de governança.

Mudanças de implementação que não afetem contratos, requisitos ou decisões aprovadas poderão seguir fluxo simplificado, conforme classificação.

## 4. Categorias de mudança

| Categoria | Código | Definição |
|---|---|---|
| Editorial | EDITORIAL | Correção de texto ou formatação sem alteração normativa |
| Documentation | DOCUMENTATION | Alteração documental que afeta organização, referências ou completude |
| Requirement | REQUIREMENT | Alteração de comportamento ou requisito |
| Architecture | ARCHITECTURE | Alteração de ADR, componente ou fronteira |
| Contract | CONTRACT | Alteração de interface, schema ou compatibilidade |
| Data | DATA | Alteração de modelo, persistência ou semântica |
| Security | SECURITY | Alteração de política, acesso ou isolamento |
| Risk | RISK | Alteração de limites ou regras financeiras |
| AI/Model | AI_MODEL | Alteração de observação, treinamento, modelo ou inferência |
| Operational | OPERATIONAL | Alteração de deployment, execução ou recuperação |
| Scope | SCOPE | Alteração de incremento, épico ou backlog |
| Emergency | EMERGENCY | Alteração urgente para conter incidente |

Uma mudança poderá pertencer a mais de uma categoria. A categoria de maior impacto deverá orientar o processo de aprovação.

## 5. Classificação de impacto

| Nível | Definição | Tratamento |
|---|---|---|
| LOW | Sem alteração de comportamento, contrato ou decisão normativa | Revisão simplificada |
| MEDIUM | Impacto limitado em documentação ou componente, sem afetar invariantes críticos | Análise de impacto e aprovação funcional |
| HIGH | Afeta contratos, requisitos, múltiplos componentes ou critérios de aceite | Revisão arquitetural/técnica e testes de regressão |
| CRITICAL | Afeta autorização financeira, risco, segurança, segregação, reconciliação ou operação LIVE | Aprovação reforçada e bloqueio da promoção até revalidação |

A classificação deverá considerar tanto o impacto direto quanto os efeitos transitivos identificados na Traceability Matrix.

## 6. Modelo de registro

Cada mudança deverá possuir:

| Campo | Descrição |
|---|---|
| Change ID | Identificador único |
| Title | Nome da mudança |
| Description | Descrição objetiva |
| Reason | Justificativa |
| Change Category | Categoria |
| Impact Level | Severidade/impacto |
| Requested By | Solicitante |
| Functional Owner | Responsável |
| Source Artifact | Artefato original |
| Source Version | Versão de origem |
| Target Version | Versão proposta |
| Affected ADRs | Decisões impactadas |
| Affected Components | Componentes impactados |
| Affected Requirements | Pendências/requisitos impactados |
| Affected Backlog | Épicos, Features e histórias impactados |
| Affected Contracts | Interfaces impactadas |
| Affected Tests | Testes a revisar ou executar |
| Affected Evidence | Evidências potencialmente invalidadas |
| Risk Assessment | Avaliação de risco |
| Migration/Rollback Plan | Plano de transição e recuperação |
| Approval Reference | Aprovação formal |
| Implementation Reference | PR/commit ou artefato |
| Validation Reference | Testes e evidências |
| Status | Estado da mudança |
| Created At | Data de criação |
| Updated At | Última atualização |

Campos não conhecidos deverão permanecer `TBD`. Não será permitido preencher referências presumidas.

## 7. Estados da mudança

| Estado | Significado |
|---|---|
| PROPOSED | Mudança solicitada |
| UNDER_ANALYSIS | Impacto em avaliação |
| IN_REVIEW | Aguardando decisão |
| APPROVED | Mudança autorizada, ainda não necessariamente aplicada |
| REJECTED | Mudança não autorizada |
| DEFERRED | Mudança postergada |
| IN_PROGRESS | Implementação da mudança |
| VALIDATING | Alteração em validação |
| COMPLETED | Implementada, validada e registrada |
| ROLLED_BACK | Alteração revertida tecnicamente |
| CANCELLED | Solicitação cancelada |
| SUPERSEDED | Substituída por outra mudança |

A aprovação de uma mudança não implica que sua implementação tenha sido concluída.

## 8. Fluxo de Change Control

1. **Solicitação:** registrar a necessidade de alteração.
2. **Classificação:** identificar categoria e impacto.
3. **Análise:** avaliar efeitos sobre requisitos, arquitetura, contratos, testes e evidências.
4. **Planejamento:** definir versão de destino, migração, rollback e validação.
5. **Revisão:** submeter a proposta à autoridade competente.
6. **Aprovação:** registrar decisão no Approval Register.
7. **Implementação:** aplicar somente o escopo aprovado.
8. **Validação:** executar testes e produzir evidências.
9. **Atualização:** sincronizar Document Registry, Traceability Matrix e Gap Register.
10. **Encerramento:** registrar versão resultante e referências verificáveis.

Mudanças rejeitadas ou postergadas deverão permanecer registradas.

## 9. Regras de versionamento

Documentos e contratos deverão utilizar versionamento consistente com a política aplicável.

Para documentos normativos, recomenda-se:

- **MAJOR:** mudança incompatível de decisão, escopo ou comportamento normativo.
- **MINOR:** adição compatível de regras, seções ou capacidades.
- **PATCH:** correção editorial ou esclarecimento sem alteração material.

Versões em revisão poderão utilizar sufixos como `draft.1`, `draft.2` e `rc.1`.

Uma versão aprovada não poderá ser substituída por conteúdo diferente mantendo o mesmo identificador de versão.

## 10. Registro inicial de mudanças históricas

Os registros abaixo documentam marcos de evolução já aprovados. São entradas históricas de governança, não solicitações de alteração ainda pendentes.

| Change ID | Marco | Origem → Resultado | Estado |
|---|---|---|---|
| CHG-BASE-001 | Consolidação global Etapa 01 | Visão arquitetural → G01–G08 | COMPLETED |
| CHG-BASE-002 | Consolidação global Etapa 02 | Componentes → G09–G18 | COMPLETED |
| CHG-BASE-003 | Consolidação global Etapa 03 | Fluxos e contratos → G19–G30 | COMPLETED |
| CHG-BASE-004 | Consolidação global Etapa 04 | MVP e priorização → G31–G40 | COMPLETED |
| CHG-BASE-005 | Consolidação global Etapa 05 | Roadmap e backlog → G41–G50 | COMPLETED |
| CHG-BASE-006 | Consolidação global Etapa 06 | Critérios e baseline final → G51–G60 | COMPLETED |
| CHG-TECH-001 | Fundação técnica I00 | Proposta → T01–T10 aprovadas | COMPLETED |
| CHG-DOC-001 | Padrão documental | Proposta → TS-DOC-STD-V1.0 | COMPLETED |
| CHG-DOC-002 | Document Registry | Proposta → TS-DOC-REG-001 | COMPLETED |
| CHG-DOC-003 | Gap Register | Proposta → TS-DOC-GAP-001 | COMPLETED |
| CHG-DOC-004 | Traceability Matrix | Proposta → TS-DOC-TRC-001 | COMPLETED |
| CHG-DOC-005 | Approval Register | Proposta → TS-DOC-APR-001 | COMPLETED |

**Nota:** essas entradas registram a evolução das decisões e documentos aprovados. Não comprovam execução de software, alteração de repositório ou testes.

As datas exatas e referências verificáveis de cada marco deverão ser associadas aos registros originais durante a auditoria documental.

## 11. Mudanças pendentes ou potenciais

As seguintes necessidades são conhecidas, mas não representam alterações aprovadas de baseline:

| Referência | Necessidade | Tratamento |
|---|---|---|
| DOC-GAP-001 | Reconciliação P01–P47 | Correção documental após conferência |
| DOC-GAP-002 | Classificação de P18 | Avaliar necessidade de revisão da classificação |
| DOC-GAP-003 | Integralidade das ADRs originais | Recuperação e verificação |
| DOC-GAP-004 | Formalização ADR-089–098 | Materialização dos registros |
| DOC-GAP-005 | Rastreabilidade integral | Complementação de vínculos |
| DOC-GAP-006 | Features e histórias I00 | Refinamento |
| DOC-GAP-007 | Verificação física de arquivos | Auditoria do repositório |
| DOC-GAP-008 | Owners e referências de aprovação | Complementação de governança |

A correção de uma lacuna não exigirá automaticamente nova ADR. Isso dependerá de haver ou não mudança material na decisão aprovada.

## 12. Análise de impacto obrigatória

Para mudanças HIGH ou CRITICAL, deverão ser avaliados:

- Componentes afetados.
- Dependências diretas e transitivas.
- Requisitos alterados.
- Contratos impactados.
- Compatibilidade entre versões.
- Modelos de dados e migrações.
- Testes necessários.
- Evidências invalidadas.
- Políticas de risco e segurança.
- Necessidade de reexecutar gates.
- Impacto no roadmap e nas entregas.
- Plano de recuperação.

A análise deverá utilizar a Traceability Matrix como fonte de relacionamentos.

## 13. Política de mudanças emergenciais

Mudanças emergenciais deverão possuir procedimento controlado, com:

- Justificativa do incidente.
- Identificação da autoridade de emergência.
- Escopo mínimo necessário.
- Avaliação dos riscos de intervenção.
- Registro da decisão.
- Testes proporcionais à criticidade.
- Plano de reversão ou recuperação.
- Revisão posterior obrigatória.

Nenhuma emergência autoriza contornar invariantes financeiros, criar credenciais LIVE não aprovadas ou promover automaticamente um modelo.

O retorno à operação após incidente deverá seguir os critérios de segurança e autorização aplicáveis.

## 14. Integração com o Codex

O Codex deverá:

- Consultar o Change Log antes de alterar artefatos aprovados.
- Identificar mudanças materiais.
- Criar propostas de alteração quando necessário.
- Apresentar análise de impacto.
- Preservar versões anteriores.
- Implementar apenas alterações autorizadas.
- Atualizar testes e documentação relacionada.
- Registrar PR, commit e evidências após execução.

O Codex não poderá:

- Aprovar mudanças por conta própria.
- Modificar ADRs aprovadas silenciosamente.
- Alterar políticas de risco sem autorização.
- Declarar mudanças concluídas sem validação.
- Reutilizar evidências de versões incompatíveis.
- Habilitar LIVE por alteração de configuração.

## 15. Indicadores de Change Management

A governança deverá acompanhar:

- Mudanças abertas por categoria.
- Mudanças por severidade.
- Tempo médio de aprovação.
- Tempo médio de implementação.
- Mudanças rejeitadas.
- Mudanças revertidas.
- Alterações sem rastreabilidade completa.
- Evidências invalidadas e pendentes de revalidação.
- Alterações emergenciais.
- Mudanças que exigem nova ADR.
- Mudanças que impactam gates G0–G5.

Os indicadores deverão ser calculados a partir dos registros reais.

## 16. Critérios de aceite deste documento

O CHANGE-LOG.md estará apto à aprovação quando:

1. Os princípios de controle de mudanças estiverem definidos.
2. As categorias de mudança estiverem estabelecidas.
3. Os níveis de impacto estiverem padronizados.
4. O modelo de registro estiver completo.
5. Os estados da mudança estiverem definidos.
6. O fluxo de Change Control estiver estabelecido.
7. As regras de versionamento estiverem definidas.
8. Os marcos históricos estiverem registrados sem confundir documentação e implementação.
9. A análise de impacto e a política de emergência estiverem estabelecidas.
10. As responsabilidades do Codex, evidências e restrições LIVE estiverem preservadas.

---

**Status:** APPROVED  
**Approval Reference:** [16/11/2026 · CHG-R01–CHG-R10 aprovadas sem ressalvas](history/TS-DOC-CHG-001/APPROVAL.md)  
**Próximo documento:** INCREMENT-TEMPLATE.md  
**Próxima etapa:** aguardar o conteúdo do INCREMENT-TEMPLATE.md.

## 17. Histórico e estado da revisão

O [anexo original](history/TS-DOC-CHG-001/IN-REVIEW.txt) e o [bloco de aprovação recebido](history/TS-DOC-CHG-001/TEXTO-DE-APROVACAO-RECEBIDO.md) estão arquivados. A versão **1.0** foi aprovada em 16/11/2026. O histórico também preserva a [revisão local anterior à aprovação](history/TS-DOC-CHG-001/REVISAO-LOCAL-IN-REVIEW.txt). Os marcos da seção 10 preservam o escopo das decisões históricas.

Para CHG-DOC-005, a [aprovação comunicada do TS-DOC-APR-001](history/TS-DOC-APR-001/APPROVAL.md) está registrada. A publicação e a conferência do texto integral aprovado na pasta oficial continuam pendentes.

[G0](G0-REVIEW-DOSSIER.md) segue em revisão e LIVE permanece indisponível.
