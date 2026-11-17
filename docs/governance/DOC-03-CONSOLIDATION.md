# Consolidação DOC-03 de I00 a I09

**12/11/2026 · IN_REVIEW.** A consolidação cobre as 24 histórias iniciais e os 14 pacotes de I00. Os vínculos por épico vêm do Blueprint. Os vínculos por história, pendência, ADR e teste nas matrizes incluem associações propostas por conteúdo, sujeitas a revisão. Os índices de origem cobrem P01–P106 e ADR-001–098. A presença de um ID ou de uma função de teste indica rastreabilidade documental. O aceite depende do resultado, do candidato e da decisão correspondente. **G0–G5 seguem abertos. LIVE permanece indisponível.**

[Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) · [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) · [Pendências](PENDING-ITEM-RECONCILIATION.md) · [ADRs](ADR-RECONCILIATION.md)

## Cobertura por incremento

| Incremento | Histórias e decisões de referência | Evidência e limite |
|---|---|---|
| I00 | TS-ST-001–004 · TS-ADR-089–098 · I00-01 a I00-14 | RC1 aceito no escopo do bundle. AC07 e AC09 parciais e AC02 com ressalva. [Matriz](DOC-03-I00-TRACEABILITY.md) |
| I01 | TS-ST-005/006 · P01/P02/P05/P06/P53/P55 · ADR-002/005/046/047 | Coleta, persistência e retomada documentadas em recortes históricos. Políticas de lacunas, atraso e revisão de origem requerem validação. [Matriz](DOC-03-I01-I02-TRACEABILITY.md) |
| I02 | TS-ST-007/008 · P03/P08/P55/P56 · ADR-003/004/047/048 | Ensaios de Market State multi-intervalo e features. Catálogo, compatibilidade, critérios de frescor e escopo SMC ainda abertos. [Matriz](DOC-03-I01-I02-TRACEABILITY.md) |
| I03 | TS-ST-009–012 · P19–P32/P96/P99 · ADR-017–028 | Simulação Spot, Futures e livro-razão com resultados de recortes identificados. Falta consolidar candidato, políticas completas, resultados integrados e decisão de aceite. [Matriz](DOC-03-I03-TRACEABILITY.md) |
| I04 | TS-ST-013/014 · P07–P18/P56/P57 · ADR-007–016/048/078 | Entradas de I02/I03 rastreadas. Falta demonstrar observação versionada, treino reproduzível, Registry, inferência e autoridade preservada. [Matriz](DOC-03-I04-TRACEABILITY.md) |
| I05 | TS-ST-015/016 · P57/P91–P95/P100 · ADR-075–078/083 | Ensaios de custos, funding e liquidação de I03 são casos de referência. Falta backtest histórico e resultado OOS e benchmarks reproduzíveis. [Matriz](DOC-03-I05-TRACEABILITY.md) |
| I06 | TS-ST-017–020 · P33–P47/P96–P99/P101 · ADR-029–040/049–052/079–081/087 | Há evidência de dependência de correlação, recuperação e reconciliação. Falta PAPER contínuo com interface, autoridade, E2E e campanha de falhas. [Matriz](DOC-03-I06-TRACEABILITY.md) |
| I07 | TS-ST-021/022 · P65–P84/P29–P32/P99/P106 · ADR-021/027/058–070/081 | Isolamento local, restore de amostra e recuperação PAPER sustentam partes dos controles. Falta prova integrada de prontidão e homologação do recorte de TS-ST-022. [Matriz](DOC-03-I07-TRACEABILITY.md) |
| I08 | TS-ST-023 · P97/P100–P104 · ADR-062/070/082–087 | RC1 oferece referência de manifesto e decisão. G3, limites, monitoramento e Go/No-Go do candidato seguem pendentes. [Matriz](DOC-03-I08-TRACEABILITY.md) |
| I09 | TS-ST-024 · P100–P106 como vínculos propostos · ADR-082–087 | Falta histórico de I08, avaliação de estabilidade, revisão de risco e nova decisão humana. [Matriz](DOC-03-I09-TRACEABILITY.md) |

## Pontos de rastreabilidade em aberto

- **P52, P62 e P64.** Os vínculos propostos foram incorporados em I00, I01 e I07. Continuam pendentes os critérios de adoção de broker, a política e o teste de restauração e as métricas e testes de capacidade do banco. [I00](DOC-03-I00-TRACEABILITY.md) · [I01/I02](DOC-03-I01-I02-TRACEABILITY.md) · [I07](DOC-03-I07-TRACEABILITY.md)
- **P56/P57/P95.** I02 fornece definições e linhagem de features, I04 depende de observações e datasets versionados e I05 depende de partições e manifestos de execução. Confirmar proprietários, schemas, versões, corte temporal, compatibilidade e teste de reprodução. P18 segue M3 provisório. [I04](DOC-03-I04-TRACEABILITY.md) · [I05](DOC-03-I05-TRACEABILITY.md)
- **Procedência do checkout.** As notas de I02 e I03 foram atualizadas com os testes multi-intervalo, as features adicionais, o dump de I01 e o método de cotação dos livros-razão PAPER no checkout oficial. Ainda é preciso ligar os artefatos e resultados integrados a um candidato identificável.
- **Revisão dos vínculos.** Confirmar com os responsáveis as associações propostas e preencher os vínculos individuais pendentes de componente, contrato, cenário e resultado. A disponibilidade de texto para 98 ADRs e 106 pendências não demonstra cobertura individual de testes ou aceite. [Decisões da reconciliação](RECONCILIATION-DECISIONS.md)

## O que precisa de validação por gate

| Gate | Validação pendente | Revisão prevista no Blueprint |
|---|---|---|
| G0 · Engineering Ready | Consolidar candidato e evidências I00–I04 de build, contratos, CI, testes, invariantes e conformidade. Tratar DOC-04 (ordenação e lacunas permanentes), DOC-05 (métricas da Outbox) e DOC-06 (dependências de release). Vincular o candidato de I03 e demonstrar Observation Builder, PPO e Registry em I04. O aceite humano de I00-14/RC1 cobre o bundle. [Consolidação DOC-07](DOC-07-RC1-ACCEPTANCE.md) | Engineering / QA |
| G1 · Strategy Validated | Aprovar dados e manifestos, hipóteses de custos, protocolo walk-forward e embargo, benchmarks e limites de P14/P100. Reproduzir resultados líquidos OOS por janela e demonstrar ausência de vazamento temporal. [I05](DOC-03-I05-TRACEABILITY.md) | Quant / AI / Risk |
| G2 · PAPER Qualified | Aprovar duração, amostra e limites (P97/P100). Demonstrar PAPER contínuo, RBAC, trilha completa, paridade lógica no recorte autorizado, reconciliação e campanha de falhas. Consolidar o bundle e as evidências aplicáveis de G0/G1. [I06](DOC-03-I06-TRACEABILITY.md) | QA / Trading / Risk |
| G3 · Operationally Ready | Aprovar e demonstrar IAM e gestão de segredos em ambiente isolado, restore com RPO/RTO, reconciliação e bloqueio/retomada por OperationalReadiness. Validar os critérios e a evidência de TS-ST-022/P106 para timeout, filtros, status e reconciliação. Os ensaios PAPER sustentam recortes parciais. [I07](DOC-03-I07-TRACEABILITY.md) | Security / SRE / Risk |
| G4 · LIVE Limited | Exige decisão humana de G3 vinculada ao candidato. Ainda faltam limites de capital/exposição, critérios de monitoramento e suspensão, bundle e parecer Go/No-Go de gestores autorizados. Os cenários permitidos permanecem em PAPER. [I08](DOC-03-I08-TRACEABILITY.md) | Gestores autorizados |
| G5 · LIVE Controlled | Exige decisão prévia de G4 e histórico de I08 conforme a baseline. Ainda faltam histórico e estabilidade dentro dos limites, nova avaliação de risco, janela e amostra aprovadas, bundle e nova decisão humana. [I09](DOC-03-I09-TRACEABILITY.md) | Gestores / Risk |

Verificação documental com PowerShell e `rg` no checkout oficial. Foram conferidos os links das nove matrizes e a existência das 45 funções de teste citadas. Nenhum resultado novo de software foi produzido nesta revisão.

[Dossiê de revisão de G0](G0-REVIEW-DOSSIER.md).
