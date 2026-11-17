# Plano de governança documental

Plano TS-DOC-GOV de 12/11/2026. O usuário aprovou o catálogo mínimo de I00 e a ordem de tratamento. A [recuperação inicial](SOURCE-RECOVERY.md) documenta o bundle, as fontes e as pendências. A função é operada pelo Codex sob demanda e mantém o [registro](DOCUMENT-REGISTRY.md), as [lacunas](DOCUMENT-GAP-ANALYSIS.md) e a [matriz](REQUIREMENTS-TRACEABILITY-MATRIX.md). O catálogo pode ser atendido por seções de documentos existentes, com links para a versão e a evidência aplicáveis.

| Ordem | Trabalho proposto | Dependência | Evidência de conclusão |
|---|---|---|---|
| 1 | Aprovar catálogo mínimo e classificação das lacunas de I00 | Revisão dos quatro documentos desta auditoria | Decisão humana registra itens obrigatórios, prioridade e responsáveis |
| 2 | Recuperar pacote RC1 e conciliar o status histórico de I00-13, I00-14 e DOC-07 | Artefatos originais e registro de aceite | Identidade e hashes verificados, referências íntegras e decisão de 11/11 indexada |
| 3 | Tratar DOC-04, DOC-05 e DOC-06. Confirmar contratos complementares exigidos | Fonte T01–T10, revisão de Engenharia e QA e catálogo I00 aprovado | Política de ordenação, métricas e avaliação de release aprovadas ou encaminhamento formal por lacuna |
| 4 | Recuperar originais de arquitetura e pendências em paralelo à preparação dos incrementos | Blueprint, Engineering Foundation e D01–D07 originais | Versões e localizadores por ID, reconciliação P01–P47 e decisão de P18. Completar DOC-03 progressivamente |
| 5 | Consolidar prontidão de I01–I04 para revisão de G0 | Contratos, testes, CI, evidências de conformidade e candidato identificável | Revisão técnica e decisão humana registrada no gate aplicável |
| 6 | Aplicar o catálogo aos incrementos seguintes antes do desenvolvimento das histórias afetadas | Escopo e dependências aprovados por incremento | Requisitos críticos com origem, contratos e critérios aprovados, lacunas bloqueantes resolvidas |

## Catálogo proposto

| Classe documental | Domínios e momento de aplicação |
|---|---|
| Arquitetura de domínio, requisitos funcionais e não funcionais, ADRs e matriz | D01–D07, por incremento e história |
| Projeto de componente e especificação de interfaces | Os 33 componentes conforme criticidade. I00 prioriza envelopes, API de diagnóstico e Outbox |
| Modelo de dados, dicionário e migrations | I00 em D05–D06. I01–I03 em D01, D03 e D05 conforme persistência |
| Máquinas de estado e regras de negócio | D03 a partir de I03. D02 a partir de I04. Detalhar cenários de erro e limites por fluxo |
| Segurança, modelo de ameaças e runbooks | I00 prioriza configuração local, isolamento, segredos e recuperação. D03–D06 ampliam conforme o incremento e as interfaces |
| Estratégia de testes, critérios de aceite e evidências | D07 e todos os componentes por incremento. Priorizar I00 e rastrear I01–I04 para G0 |

## Operação da função

### Documentos de arquitetura e domínio

`docs/architecture/` já contém a visão inicial. As próximas visões por incremento devem documentar fluxos, componentes, fronteiras e interfaces, começando pelo Trading Core PAPER e sua dependência de Market State. `docs/domains/` receberá especificações em DRAFT por domínio e recorte. Para D03, a [matriz de I03](DOC-03-I03-TRACEABILITY.md) orienta os primeiros documentos de Control e Risk, execução simulada e reconciliação do Portfolio. As políticas e regras ainda sem decisão entram com referência à pendência correspondente. `docs/adr/` receberá fichas individuais com contexto, alternativas e consequências sustentados pelas fontes ou por revisão humana. O [índice reconciliado](ADR-RECONCILIATION.md) já localiza as decisões disponíveis.

1. Fixar recorte, fontes e versões. Identificar requisito e localização original antes de vinculá-lo a uma história.
2. Inventariar os documentos e revisar cobertura, consistência, dependências e evidência de aprovação. Registrar lacuna com impacto, responsável proposto e condição de resolução.
3. Submeter prioridades e documentos obrigatórios à aprovação. Após autorização, preparar especificações em DRAFT usando fontes recuperadas e registrar decisões de mudança conforme AGENTS.md.
4. Atualizar status por versão e guardar o registro da decisão humana. Calcular cobertura por incremento com denominador de itens obrigatórios aprovado e contagens de presentes, aprovados, requisitos críticos com fonte e lacunas bloqueantes.
5. Declarar Documentation Ready quando os documentos obrigatórios estiverem aprovados, requisitos críticos tiverem origem rastreada e lacunas bloqueantes estiverem resolvidas. Registrar gate e release em decisões próprias. LIVE permanece indisponível.

## Próximas ações

O bundle e as fontes principais foram recuperados. As pendências e ADRs estão indexadas por ID. Tratar DOC-04 a DOC-06 na ordem aprovada e completar os vínculos de DOC-03 progressivamente. P18 segue M3 provisório e as decisões de escopo e de evidência estão no [registro da reconciliação](RECONCILIATION-DECISIONS.md).
