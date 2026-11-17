# TS-ST-001 — Monorepo Bootstrap

## 1. Identificação

| Campo | Valor |
|---|---|
| Story ID | TS-ST-001 |
| Versão da especificação | 0.1 |
| Estado documental | APPROVED |
| Estado do trabalho | IDENTIFIED |
| Incremento | I00 — Engineering Foundation |
| Épico principal | [TS-EP-01 — Engineering Foundation](../epics/TS-EP-01.md) |
| Feature principal | [I00-FEAT-001](../features/I00-FEAT-001.md) · vínculo APPROVED |
| Domínio principal | D07 — Engenharia, Qualidade e Validação |
| Componente | D07-C01, conforme DOC-03 I00 |
| Responsabilidade funcional | Engineering Architecture |
| Responsáveis técnico e QA | TBD |
| Prioridade | Primeira história na sequência recomendada de I00 |
| Estimativa | TBD |
| Aprovação da ficha | Aprovada pelo usuário em 17/11/2026 |
| Última atualização | 17/11/2026 |

## 2. História técnica

A descrição original é “Criar estrutura de repositório e módulos”. O resultado esperado é a estrutura inicial do monorepo, com fronteiras identificáveis e verificações executáveis em CI. “Monorepo Bootstrap” é o título de trabalho registrado no épico. [Blueprint, linhas 2019 e 3137](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)

## 3. Contexto arquitetural

Aplicam-se TS-ARCH-GLOBAL-V1.0, TS-ENG-I00-V1.0, [TS-INC-I00-001](../increments/I00-INCREMENT.md) e TS-EP-01. O recorte estrutural I00-01 referencia TS-ADR-089, TS-ADR-090 e TS-ADR-098 no registro mestre. P85 é origem de estrutura e padrões; P88 dá apoio de qualidade. Vínculos aprovados pelo usuário em 17/11/2026. Vínculo direto com F01–F10 em aberto. [DOC-03 I00](../governance/DOC-03-I00-TRACEABILITY.md)

## 4. Escopo

Organizar o repositório modular e suas áreas de aplicações, pacotes, contratos, testes e documentação conforme I00-FEAT-001. Toolchain, lockfile e pipeline entram pelos pacotes de apoio. A especificação de contratos Command/Event pertence a TS-ST-002. O recorte é de fundação local e CI.

## 5. Pré-condições

Usar a estrutura normativa da Feature e identificar o checkout ou candidato que servirá para a revisão. A designação dos responsáveis e os parâmetros exatos do ambiente de verificação estão pendentes.

## 6. Comportamento esperado

Em um checkout limpo, a equipe consegue localizar os módulos, executar a verificação de imports e rodar build e testes em CI com o apoio da toolchain. Uma falha de import, build ou teste deve aparecer no resultado da verificação. Os módulos preservam as fronteiras previstas na Feature.

## 7. Contratos e interfaces

O recorte usa a organização dos pacotes e seus pontos de importação. A definição de APIs e schemas é tratada pelas histórias e Features correspondentes.

## 8. Dados e persistência

As verificações estruturais usam o conteúdo versionado do repositório. Persistência de domínio fica no escopo próprio de I00.

## 9. Requisitos não funcionais

Estrutura modular, fronteiras explícitas e build reproduzível, conforme I00-FEAT-001 e I00-AC01.

## 10. Dependências

| Pacote | Papel na história | Precedência de engenharia |
|---|---|---|
| I00-01 | Recorte principal de estrutura e imports. Corresponde a I00-FEAT-001. | Sem predecessora de pacote registrada |
| I00-02 | Apoio de toolchain, lockfile e verificações de qualidade | Depende de I00-01 |
| I00-11 | Apoio transversal de CI e build | Depende de I00-02 |

[Engineering Foundation, linhas 714–724](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>)

## 11. Critérios de aceite

**Critério original:** “Build e testes executáveis em CI”.

A decomposição aprovada desse critério é conferir a árvore modular e os imports esperados, executar a instalação e o build com a toolchain versionada e vincular a execução de CI ao commit avaliado. [Registro mestre I00](registro-mestre-i00.md)

### Critérios detalhados — APPROVED

Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

| ID | Verificação | Resultado esperado | Evidência |
|---|---|---|---|
| ST001-AC01 | Estrutura e fronteiras | A árvore de diretórios e os pontos de importação correspondem ao recorte de I00-FEAT-001; a revisão registra os módulos esperados e eventuais desvios. | Árvore versionada e verificação de imports. |
| ST001-AC02 | Instalação reproduzível | Um checkout limpo instala as dependências a partir do lockfile aplicável e produz o artefato de build com a toolchain identificada. | Comandos, versões e logs de instalação e build. |
| ST001-AC03 | CI verificável | Build e testes aplicáveis executam no mesmo commit e o pipeline sinaliza falha quando uma dessas verificações falha. | URL ou identificação da execução e resultados por etapa. |
| ST001-AC04 | Rastreabilidade | O registro relaciona I00-01, I00-02 e I00-11 aos resultados apresentados, com revisão técnica e de QA. | Registro por pacote e parecer de revisão. |

## 12. Estratégia de testes

Usar a verificação de imports para o recorte I00-01 e as verificações de toolchain, build e CI para os recortes I00-02 e I00-11. O registro mestre identifica as referências de verificação por pacote.

## 13. Dados e ambiente de teste

Checkout limpo e ambiente local ou de CI de I00, com versões de ferramentas conforme o lockfile aplicável. Candidato para aceite da ficha e da entrega a definir.

## 14. Observabilidade

Preservar o resultado de build e testes na execução de CI e relacioná-lo ao commit revisado.

## 15. Segurança e risco

Aplica-se a segregação da fundação I00 conforme TS-ADR-098. Usar ambiente local ou de CI no recorte desta história. [Segurança e aceite de I00](../04-SEGURANCA-E-ACEITE.md)

## 16. Definition of Ready

Para declarar a história pronta, revisar o escopo e os critérios, definir responsáveis, validar as associações por requisito e identificar o ambiente de verificação. O candidato será identificado para o aceite da entrega.

## 17. Plano de implementação

Sequência de referência para revisão da história: conferir a estrutura I00-01, preparar as verificações de I00-02 e executar o pipeline I00-11 conforme a ordem registrada no Engineering Foundation.

## 18. Evidências de implementação

O [registro mestre I00](registro-mestre-i00.md) e a [evidência de bootstrap](../evidence/I00-bootstrap.md) documentam verificações históricas. A referência de aceite desta ficha e o candidato correspondente ficam pendentes.

## 19. Definition of Done

Estrutura revisada, build e testes de CI vinculados ao commit avaliado, evidências registradas e aceite da entrega documentado.

## 20. Riscos e lacunas

Responsáveis e estimativa em aberto. Vínculos P85/P88 aprovados. Dependências específicas da história aguardam conferência. A precedência de engenharia por pacote está registrada na seção 10.

## 21. Rastreabilidade

I00 → TS-EP-01 → **I00-FEAT-001 → TS-ST-001**. Vínculo principal confirmado pelo usuário nesta conversa em 17/11/2026. I00-02 apoia toolchain e qualidade. I00-11 apoia CI e build. [DOC-03 I00](../governance/DOC-03-I00-TRACEABILITY.md)

## 22. Histórico de alterações

17/11/2026 · Versão 0.1 · Criação da ficha a partir das fontes reconciliadas em R03, seguindo o [template de histórias](../governance/templates/STORY-TEMPLATE.md).

## 23. Registro de aprovação

**APPROVED** · Aprovação comunicada pelo usuário nesta conversa em 17/11/2026.


### Decisão de vínculos de histórias — 17/11/2026

O usuário aprovou nesta conversa os vínculos de escopo das histórias TS-ST-001–004 conforme o catálogo de Features. Registro aplicado às referências correspondentes neste documento.

### Responsabilidades, requisitos e revisão de aceite — 17/11/2026

Responsabilidade funcional e vínculos aprovados pelo usuário. P85 como origem de estrutura e padrões; P88 como apoio de qualidade. Critérios detalhados aprovados pelo usuário nesta conversa em 17/11/2026.

### Aprovação dos critérios detalhados — 17/11/2026

O usuário aprovou os critérios detalhados desta ficha. O aceite da entrega depende da verificação das evidências e da decisão correspondente.

### Decisão de escopo — APPROVED — 17/11/2026

Aprovado o mapeamento físico existente com src/trade_system e apps/api para o recorte de TS-ST-001. A correspondência com a árvore proposta de I00-FEAT-001 fica documentada no inventário. As nove importações entre módulos identificadas aguardam revisão das fronteiras.

Aprovação comunicada pelo usuário nesta conversa. Base técnica examinada: 0172728bd36c23247987a28c0fdccd32488e06f3. [Inventário de escopo](../evidence/ts-st-001-004-0172728/INVENTARIOS-ESCOPO.md).
### Perfil de cliente PostgreSQL — APPROVED — 17/11/2026

O usuário aprovou Linux/Alpine sem LDAP/GSSAPI e autorizou aplicação com
preservação do fluxo Windows e novas verificações antes do commit candidato.
O aceite de segurança e da entrega permanece em revisão.
[Decisão e limites](../governance/AC02-CLIENT-PROFILE.md).