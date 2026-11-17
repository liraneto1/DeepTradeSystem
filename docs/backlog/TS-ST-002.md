# TS-ST-002 — Versioned Contracts

## 1. Identificação

| Campo | Valor |
|---|---|
| Story ID | TS-ST-002 |
| Versão da especificação | 0.1 |
| Estado documental | APPROVED |
| Estado do trabalho | IDENTIFIED |
| Incremento | I00 — Engineering Foundation |
| Épico principal | [TS-EP-01](../epics/TS-EP-01.md) |
| Feature principal | [I00-FEAT-003](../features/I00-FEAT-003.md) · vínculo APPROVED |
| Domínio principal | D07, com participação de D05 |
| Responsabilidade funcional | Engineering Architecture |
| Responsáveis técnico e QA | TBD |
| Prioridade | 2ª história na sequência recomendada de I00 |
| Estimativa | TBD |
| Aprovação da ficha | Aprovada pelo usuário em 17/11/2026 |
| Última atualização | 17/11/2026 |

## 2. História técnica

A descrição original é “Definir schemas versionados de comandos e eventos”. O título de trabalho consta do épico. [Blueprint, linha 2020](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)

## 3. Contexto arquitetural

Aplicam-se TS-ARCH-GLOBAL-V1.0 e TS-ENG-I00-V1.0. D05-C02, D07-C02 · TS-ADR-097/098. P90 é origem principal; P61 é dependência temática. Vínculos aprovados pelo usuário em 17/11/2026. Vínculos individuais com fluxos permanecem em conferência. [DOC-03 I00](../governance/DOC-03-I00-TRACEABILITY.md)

## 4. Escopo

Versionar CommandEnvelope v1 e EventEnvelope v1 e validar os exemplos de referência.

## 5. Pré-condições

Schemas v1 e exemplos sintéticos disponíveis para validação.

## 6. Comportamento esperado

Validar exemplos contra o schema correspondente. Conferir campos obrigatórios, versão e timestamps UTC. Registrar a rejeição de exemplos inválidos.

## 7. Contratos e interfaces

CommandEnvelope v1 e EventEnvelope v1, conforme a especificação de contratos.

## 8. Dados e persistência

Exemplos sintéticos dos envelopes e versões dos schemas.

## 9. Requisitos não funcionais

Validação reproduzível e versão explícita em cada envelope.

## 10. Dependências

I00-03 depende de I00-01. O catálogo registra I00-FEAT-001 e I00-FEAT-002 como dependências de I00-FEAT-003. [Engineering Foundation](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>)

## 11. Critérios de aceite

**Critério original:** “Testes de contrato e compatibilidade”. A estratégia de testes e os critérios detalhados abaixo foram aprovados pelo usuário em 17/11/2026.

### Critérios detalhados — APPROVED

Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

| ID | Verificação | Resultado esperado | Evidência |
|---|---|---|---|
| ST002-AC01 | Exemplos válidos | Exemplos sintéticos de CommandEnvelope v1 e EventEnvelope v1 passam na validação dos respectivos schemas. | Resultado por envelope e versão. |
| ST002-AC02 | Rejeição determinística | Casos com campos obrigatórios ausentes, tipos inválidos, timestamps fora do formato UTC e ambientes não permitidos são rejeitados conforme o contrato. | Matriz de entradas e resultados esperados e observados. |
| ST002-AC03 | Política de compatibilidade | Uma política identifica versões suportadas, comportamento para campos adicionais e versões desconhecidas e alterações que exigem nova versão. A política recebe revisão antes do aceite técnico. | Política versionada e decisão registrada. |
| ST002-AC04 | Compatibilidade demonstrada | A matriz produtor/consumidor testa as combinações prometidas pela política e demonstra a detecção de mudanças incompatíveis, incluindo remoção de campo obrigatório, alteração de tipo e restrição de valores. | Matriz de versões e relatório dos testes. |
| ST002-AC05 | Cobertura delimitada | O relatório identifica o recorte de P90 e P61 coberto pelos envelopes e registra contratos de domínio ainda pendentes. | Rastreabilidade dos contratos e limites de cobertura. |

## 12. Estratégia de testes

Executar testes de contrato com entradas válidas e inválidas. Definir e revisar os casos de compatibilidade aplicáveis antes do aceite.

## 13. Dados e ambiente de teste

Validação local ou em CI com exemplos sintéticos e versão de schema identificada.

## 14. Observabilidade

Associar falhas de validação à versão do schema e ao caso de teste.

## 15. Segurança e risco

Validar os ambientes permitidos nos contratos conforme I00-AC10.

## 16. Definition of Ready

Confirmar responsáveis técnicos e de QA, dependências da história e ambiente de verificação.

## 17. Plano de implementação

Conferir os envelopes v1, validar exemplos e revisar a cobertura de compatibilidade.

## 18. Evidências de implementação

Referências históricas por pacote. Candidato e evidência de aceite da história a definir. [I00-03-contratos](../evidence/I00-03-contratos.md)

## 19. Definition of Done

Critério original demonstrado no candidato, evidências vinculadas e aceite registrado.

## 20. Riscos e lacunas

Política e casos de compatibilidade entre versões a confirmar. A evidência histórica cobre recortes de v1.

## 21. Rastreabilidade

I00-FEAT-003 principal. Vínculos APPROVED pelo usuário em 17/11/2026. [Catálogo](../increments/I00-FEATURE-CATALOG.md) e [registro mestre](registro-mestre-i00.md).

## 22. Histórico de alterações

17/11/2026 · Versão 0.1 · Criação a partir das fontes reconciliadas em R03, seguindo [TS-ST-001](TS-ST-001.md).

## 23. Registro de aprovação

**APPROVED** · Aprovação comunicada pelo usuário nesta conversa em 17/11/2026.

### Decisão de vínculos de histórias — 17/11/2026

O usuário aprovou nesta conversa os vínculos de escopo das histórias TS-ST-001–004 conforme o catálogo de Features. Registro aplicado às referências correspondentes neste documento.

### Responsabilidades, requisitos e revisão de aceite — 17/11/2026

Responsabilidade funcional e vínculos aprovados pelo usuário. P90 como origem principal; P61 como dependência temática de contratos e compatibilidade. Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

### Aprovação dos critérios detalhados — 17/11/2026

O usuário aprovou os critérios detalhados desta ficha. O aceite da entrega depende da verificação das evidências e da decisão correspondente.

### Política de compatibilidade inicial — APPROVED

Aprovada pelo usuário nesta conversa em 17/11/2026 como referência inicial.

- Suporte explícito à versão exata 1.0.0 dos envelopes, com seleção do schema pelo consumidor.
- Campos adicionais na raiz são rejeitados conforme additionalProperties=false. Adições opcionais exigem avaliação dos consumidores existentes.
- Remoção de campo obrigatório, alteração de tipo ou mudança incompatível de significado exige nova versão principal.
- Mudanças no payload seguem contrato específico do conteúdo. O envelope verifica que payload é um objeto.
- A matriz produtor/consumidor deve cobrir a versão suportada, versões desconhecidas, campos adicionais e mudanças incompatíveis.

[Matriz dos 20 critérios](../governance/TS-ST-001-004-EVIDENCE-MATRIX.md)


### Decisão de escopo — APPROVED — 17/11/2026

Confirmado o recorte de aceite de TS-ST-002 pelos dois envelopes CommandEnvelope v1 e EventEnvelope v1. Contratos de conteúdo de payload e schema registry permanecem como cobertura remanescente de P61/P90.

Aprovação comunicada pelo usuário nesta conversa. Base técnica examinada: 0172728bd36c23247987a28c0fdccd32488e06f3. [Inventário de escopo](../evidence/ts-st-001-004-0172728/INVENTARIOS-ESCOPO.md).