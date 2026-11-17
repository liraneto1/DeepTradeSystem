# TS-ST-004 — Dispatcher & Idempotent Consumers

## 1. Identificação

| Campo | Valor |
|---|---|
| Story ID | TS-ST-004 |
| Versão da especificação | 0.1 |
| Estado documental | APPROVED |
| Estado do trabalho | IDENTIFIED |
| Incremento | I00 — Engineering Foundation |
| Épico principal | [TS-EP-02](../epics/TS-EP-02.md) |
| Feature principal | [I00-FEAT-006](../features/I00-FEAT-006.md) · vínculo APPROVED |
| Domínio principal | D05 — Data, Events & Audit |
| Responsabilidade funcional | Data & Event Architecture |
| Responsáveis técnico e QA | TBD |
| Prioridade | 4ª história na sequência recomendada de I00 |
| Estimativa | TBD |
| Aprovação da ficha | Aprovada pelo usuário em 17/11/2026 |
| Última atualização | 17/11/2026 |

## 2. História técnica

A descrição original é “Implementar dispatcher e consumidores”. O título de trabalho consta do épico. [Blueprint, linha 2022](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)

## 3. Contexto arquitetural

Aplicam-se TS-ARCH-GLOBAL-V1.0 e TS-ENG-I00-V1.0. D05-C02/C06 · TS-ADR-090/093/096. P50, P51 e P60 vinculados ao recorte de dispatcher e consumo, por aprovação do usuário em 17/11/2026. I00-13 dá apoio de resiliência. Vínculos individuais com fluxos permanecem em conferência. [DOC-03 I00](../governance/DOC-03-I00-TRACEABILITY.md)

## 4. Escopo

Publicar eventos persistidos na Outbox e consumir entregas com efeito idempotente.

## 5. Pré-condições

Outbox de I00-05, contratos v1 e persistência local disponíveis.

## 6. Comportamento esperado

Publicar eventos pendentes, registrar progresso e retomar após falha. Validar que entrega repetida não reaplica o efeito do consumidor.

## 7. Contratos e interfaces

EventEnvelope v1, registros Outbox e mecanismos de progresso descritos em I00-06/07.

## 8. Dados e persistência

Eventos sintéticos, registro de publicação e estado de deduplicação do consumidor.

## 9. Requisitos não funcionais

Preservar ordenação por agregado no recorte aplicável e idempotência do efeito, conforme I00-AC06/07/08.

## 10. Dependências

I00-06 depende de I00-05. I00-07 depende de I00-06. I00-13 fornece apoio transversal a cenários de recuperação. [Engineering Foundation](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>)

## 11. Critérios de aceite

**Critério original:** “Deduplicação, retry e checkpoint testados”. A estratégia de testes e os critérios detalhados abaixo foram aprovados pelo usuário em 17/11/2026.

### Critérios detalhados — APPROVED

Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

| ID | Verificação | Resultado esperado | Evidência |
|---|---|---|---|
| ST004-AC01 | Publicação e progresso | Eventos elegíveis são publicados com identidade preservada e progresso durável. A retomada após interrupção evita perda silenciosa e permite reentrega segura. | Logs correlacionados, estado persistido e teste de reinício. |
| ST004-AC02 | Consumo idempotente | Entregas repetidas, concorrentes e após reinício produzem um único efeito confirmado. Efeito e deduplicação fazem commit ou rollback conjuntamente. | Consultas de efeito e deduplicação e resultados dos testes. |
| ST004-AC03 | Retry e retenção | Falhas transitórias permitem recuperação; exaustão das tentativas mantém o evento recuperável. Tentativas, intervalos e retenção são identificados e aprovados antes do aceite. | Configuração versionada e cenários de falha transitória e persistente. |
| ST004-AC04 | Ordenação e bloqueio | Predecessor ausente bloqueia o agregado afetado sem consumir tentativas por essa espera; agregados independentes avançam. Chegada tardia e reinício preservam a sequência. | Cenários DOC-04 com estados por agregado. |
| ST004-AC05 | Reconciliação e retomada | Conflitos e suspeitas de lacuna geram registro durável. A retomada verifica a cadeia e os efeitos aplicados e registra a autoridade responsável conforme DOC-04. | Trilha de incidente, reparo, autorização e replay idempotente. |
| ST004-AC06 | Métricas | Backlog e categorias conferem com o mesmo snapshot; atraso inclui espera e retry; falha de coleta é distinguível de fila vazia e há segregação por ambiente. | Amostra conhecida e valores esperados e observados conforme DOC-05. |

## 12. Estratégia de testes

Testar entrega duplicada, retry após falha, retomada após interrupção, ordenação e checkpoint no candidato identificado.

## 13. Dados e ambiente de teste

Ambiente local com PostgreSQL e eventos sintéticos, incluindo duplicação e falha simulada.

## 14. Observabilidade

Correlacionar publicação, tentativas, consumo e retomada no recorte de I00-AC09.

## 15. Segurança e risco

Aplicar a segregação do ambiente de I00 e usar eventos sintéticos nas verificações.

## 16. Definition of Ready

Confirmar responsáveis técnicos e de QA, dependências da história e ambiente de verificação.

## 17. Plano de implementação

Conferir a publicação com I00-06 e o consumo com I00-07. Revisar as evidências de recuperação de I00-13.

## 18. Evidências de implementação

Referências históricas por pacote. Candidato e evidência de aceite da história a definir. [I00-06-dispatcher](../evidence/I00-06-dispatcher.md) · [I00-07-consumidor](../evidence/I00-07-consumidor.md) · [I00-13-resiliencia](../evidence/I00-13-resiliencia.md)

## 19. Definition of Done

Critério original demonstrado no candidato, evidências vinculadas e aceite registrado.

## 20. Riscos e lacunas

Ordenação em lacunas permanentes e quarentena dependem do recorte DOC-04. Telemetria e métricas dependem do recorte DOC-05.

## 21. Rastreabilidade

I00-FEAT-006 principal; I00-FEAT-007 vinculada ao escopo obrigatório de deduplicação do consumidor e ao aceite da história. Vínculos APPROVED pelo usuário em 17/11/2026. [Catálogo](../increments/I00-FEATURE-CATALOG.md) e [registro mestre](registro-mestre-i00.md).

## 22. Histórico de alterações

17/11/2026 · Versão 0.1 · Criação a partir das fontes reconciliadas em R03, seguindo [TS-ST-001](TS-ST-001.md).

## 23. Registro de aprovação

**APPROVED** · Aprovação comunicada pelo usuário nesta conversa em 17/11/2026.

### Decisão de vínculos de histórias — 17/11/2026

O usuário aprovou nesta conversa os vínculos de escopo das histórias TS-ST-001–004 conforme o catálogo de Features. Registro aplicado às referências correspondentes neste documento.

### Responsabilidades, requisitos e revisão de aceite — 17/11/2026

Responsabilidade funcional e vínculos aprovados pelo usuário. P50, P51 e P60 no recorte de dispatcher, ordenação e consumo idempotente. Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

### Aprovação dos critérios detalhados — 17/11/2026

O usuário aprovou os critérios detalhados desta ficha. O aceite da entrega depende da verificação das evidências e da decisão correspondente.

### Parâmetros operacionais iniciais — APPROVED

Aprovados pelo usuário nesta conversa em 17/11/2026 como referência inicial de verificação em TRAINING/PAPER.

| Parâmetro | Referência inicial |
|---|---|
| Tentativas de publicação | 5 tentativas totais |
| Espera após falhas anteriores à última tentativa | 1, 2, 4 e 8 segundos, sem jitter explícito |
| Pausa sem evento elegível | 1 segundo |
| Escalonamento de predecessor ausente | 3.600 segundos desde enqueued_at do sucessor |
| Espera pelo predecessor | Preserva tentativas |
| Retenção de evento publicado | Mínimo de 30 dias; remoção manual sujeita à elegibilidade e autorização |
| Janela de métricas | 300 segundos para comparação inicial |
| Retomada | Papéis específicos e decisão registrada |

Frequência de coleta, limiares de alerta, operadores individuais e conferência das permissões no ambiente escolhido ficam pendentes. A janela inicial será revista com base nos ensaios.

[Matriz dos 20 critérios](../governance/TS-ST-001-004-EVIDENCE-MATRIX.md)
