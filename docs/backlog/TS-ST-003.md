# TS-ST-003 — PostgreSQL & Transactional Outbox

## 1. Identificação

| Campo | Valor |
|---|---|
| Story ID | TS-ST-003 |
| Versão da especificação | 0.1 |
| Estado documental | APPROVED |
| Estado do trabalho | IDENTIFIED |
| Incremento | I00 — Engineering Foundation |
| Épico principal | [TS-EP-02](../epics/TS-EP-02.md) |
| Feature principal | [I00-FEAT-005](../features/I00-FEAT-005.md) · vínculo APPROVED |
| Domínio principal | D05 — Data, Events & Audit |
| Responsabilidade funcional | Data & Event Architecture |
| Responsáveis técnico e QA | TBD |
| Prioridade | 3ª história na sequência recomendada de I00 |
| Estimativa | TBD |
| Aprovação da ficha | Aprovada pelo usuário em 17/11/2026 |
| Última atualização | 17/11/2026 |

## 2. História técnica

A descrição original é “Implementar PostgreSQL Outbox”. O título de trabalho consta do épico. [Blueprint, linha 2021](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)

## 3. Contexto arquitetural

Aplicam-se TS-ARCH-GLOBAL-V1.0 e TS-ENG-I00-V1.0. D05-C01/C02 · TS-ADR-092/093/095. P48, P49 e P50 vinculados ao recorte de PostgreSQL e Outbox, por aprovação do usuário em 17/11/2026. Vínculos individuais com fluxos permanecem em conferência. [DOC-03 I00](../governance/DOC-03-I00-TRACEABILITY.md)

## 4. Escopo

Preparar PostgreSQL e migrações com I00-04 e registrar estado mais evento Outbox em I00-05.

## 5. Pré-condições

Instância local de PostgreSQL, migrações aplicáveis e contratos v1 disponíveis.

## 6. Comportamento esperado

Na mesma transação, gravar o estado e o evento Outbox. Conferir persistência conjunta no commit e rollback conjunto em caso de falha.

## 7. Contratos e interfaces

Registro Outbox e EventEnvelope v1 no recorte documentado.

## 8. Dados e persistência

Dados sintéticos e estado transacional sob a mesma unidade de commit do evento.

## 9. Requisitos não funcionais

Migrações reproduzíveis e integridade transacional conforme I00-AC04/05/08.

## 10. Dependências

I00-04 depende de I00-01. I00-05 depende de I00-03 e I00-04. [Engineering Foundation](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>)

## 11. Critérios de aceite

**Critério original:** “Estado e outbox persistidos atomicamente”. A estratégia de testes e os critérios detalhados abaixo foram aprovados pelo usuário em 17/11/2026.

### Critérios detalhados — APPROVED

Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

| ID | Verificação | Resultado esperado | Evidência |
|---|---|---|---|
| ST003-AC01 | Migrações | As migrações do recorte aplicam sobre banco de teste limpo e sua reversão é verificada até o ponto suportado pelo plano de migração. | Versões, comandos e estado do banco antes e depois. |
| ST003-AC02 | Commit atômico | Uma operação de teste confirma conjuntamente a mudança de estado e seu registro Outbox na mesma transação. | Consulta do estado e da Outbox após commit. |
| ST003-AC03 | Rollback atômico | Uma falha injetada entre as gravações, ou antes do commit, deixa ambos os efeitos sem persistência. | Estado esperado e observado após rollback. |
| ST003-AC04 | Duplicidade e conflito | Replay equivalente preserva efeito único. IDs distintos na mesma versão ou conteúdo divergente para o mesmo ID recebem o tratamento definido em DOC-04; a evidência de conflito sobrevive ao rollback. | Casos equivalentes, divergentes e concorrentes no escopo ambiente/conta/agregado. |
| ST003-AC05 | Ownership e concorrência | O recorte identifica o proprietário da escrita e a unidade transacional; ensaios concorrentes demonstram que as constraints preservam as identidades e limites aprovados. | Modelo de ownership, constraints e resultados concorrentes. |

## 12. Estratégia de testes

Cobrir aplicação e reversão das migrações, commit conjunto, rollback conjunto e rejeição de evento duplicado no recorte histórico.

## 13. Dados e ambiente de teste

PostgreSQL local e dados sintéticos, com schema e candidato identificados.

## 14. Observabilidade

Correlacionar evento e resultado da transação nas evidências de verificação.

## 15. Segurança e risco

Segregar a instância de teste conforme a fundação I00.

## 16. Definition of Ready

Confirmar responsáveis técnicos e de QA, dependências da história e ambiente de verificação.

## 17. Plano de implementação

Conferir migrações de I00-04 e validar a transação de I00-05 antes de avaliar commit e rollback.

## 18. Evidências de implementação

Referências históricas por pacote. Candidato e evidência de aceite da história a definir. [I00-04-postgresql](../evidence/I00-04-postgresql.md) · [I00-05-outbox](../evidence/I00-05-outbox.md)

## 19. Definition of Done

Critério original demonstrado no candidato, evidências vinculadas e aceite registrado.

## 20. Riscos e lacunas

Confirmar ownership e limites transacionais por domínio. Publicação e consumo são tratados na ficha TS-ST-004.

## 21. Rastreabilidade

I00-FEAT-005 principal; I00-FEAT-004 como dependência de PostgreSQL e migrações. Vínculos APPROVED pelo usuário em 17/11/2026. [Catálogo](../increments/I00-FEATURE-CATALOG.md) e [registro mestre](registro-mestre-i00.md).

## 22. Histórico de alterações

17/11/2026 · Versão 0.1 · Criação a partir das fontes reconciliadas em R03, seguindo [TS-ST-001](TS-ST-001.md).

## 23. Registro de aprovação

**APPROVED** · Aprovação comunicada pelo usuário nesta conversa em 17/11/2026.

### Decisão de vínculos de histórias — 17/11/2026

O usuário aprovou nesta conversa os vínculos de escopo das histórias TS-ST-001–004 conforme o catálogo de Features. Registro aplicado às referências correspondentes neste documento.

### Responsabilidades, requisitos e revisão de aceite — 17/11/2026

Responsabilidade funcional e vínculos aprovados pelo usuário. P48, P49 e P50 no recorte de PostgreSQL e Outbox. Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

### Aprovação dos critérios detalhados — 17/11/2026

O usuário aprovou os critérios detalhados desta ficha. O aceite da entrega depende da verificação das evidências e da decisão correspondente.

### Decisão de escopo — APPROVED — 17/11/2026

Confirmado o recorte de TS-ST-003 pelo produtor sintético ensaiado, com um evento por versão. Cada produtor operacional deverá ter validação completa do envelope antes de append_event e fonte autoritativa de recuperação definida ao ser integrado.

Aprovação comunicada pelo usuário nesta conversa. Base técnica examinada: 0172728bd36c23247987a28c0fdccd32488e06f3. [Inventário de escopo](../evidence/ts-st-001-004-0172728/INVENTARIOS-ESCOPO.md).