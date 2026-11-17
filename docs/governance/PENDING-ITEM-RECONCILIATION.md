# Reconciliação de P01 a P106

Registro de governança de 12/11/2026 em `IN_REVIEW`. O domínio fornece a descrição e a área indicada. O [Architecture & MVP Blueprint](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>), Etapa 04, fornece a fase primária. As linhas referem-se aos arquivos TXT recuperados. Quando a fonte tem duas tabelas, a descrição de origem preserva o texto da primeira, e o resumo do domínio registra a variante posterior quando a redação muda. A área indicada é funcional. Os registros examinados não atribuem responsáveis nominais por ID.

Distribuição conferida: **68 M0, 28 M1, 9 M2 e 1 M3 provisório (P18)**. As antecipações de partes críticas seguem G40 e as ressalvas do Blueprint. O registro não altera escopo, fase nem estado de implementação. Veja [divergências e decisões pendentes](RECONCILIATION-DECISIONS.md).

## D01

Fonte de domínio: [Domínio 01 - Integração e Dados de Mercado](<../referencias/originais/Domínio 01 - Integração e Dados de Mercado.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P01 | Inventário de endpoints Binance Spot/Futures | — | Especificação D01 | 298 | M0 · 1496 |
| P02 | Schemas, contratos e versionamento dos dados | — | Engenharia D01 | 299 | M0 · 1496 |
| P03 | Regras matemáticas de BOS, CHoCH, OB e FVG | — | Feature Engineering | 300 | M0 · 1496 |
| P04 | Frequência e retenção dos dados de order book | — | Engenharia D01 | 301 | M0 · 1496 |
| P05 | Política de lacunas, dados atrasados e recuperação | — | Engenharia D01 | 302 | M0 · 1496 |
| P06 | Estrutura PostgreSQL e eventual extensão temporal | — | Engenharia de Dados | 303 | M0 · 1496 |
| P07 | Definição exata do vetor de observação | — | Domínio 02 | 304 | M0 · 1496 |
| P08 | Política de versionamento e disponibilidade das features | — | Domínios 01 e 02 | 305 | M1 · 1498 |

## D02

Fonte de domínio: [Domínio 02 - Inteligência Artificial e Aprendizado](<../referencias/originais/Domínio 02 - Inteligência Artificial e Aprendizado.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P09 | Definir dimensões, janelas e normalização do Observation Space | Dimensões, janelas e normalização do Observation Space | Observation Builder | 351, 496 | M0 · 1502 |
| P10 | Especificar ações válidas para Spot e Futures e transições de posição | Ações válidas por mercado e transições de posição | Trading Agent | 352, 497 | M0 · 1502 |
| P11 | Formalizar a Reward Function e seus coeficientes | Formulação definitiva da Reward Function | Learning Engine | 353, 498 | M0 · 1502 |
| P12 | Definir fidelidade, limitações e validação do simulador | Fidelidade e validação do simulador | Trading Environment | 354, 499 | M0 · 1502 |
| P13 | Estabelecer datasets e metodologia de walk-forward | Datasets e metodologia walk-forward | Learning Engine | 355, 500 | M0 · 1502 |
| P14 | Definir métricas e critérios mínimos de aprovação | Métricas e critérios mínimos de aprovação | Model Evaluation | 356, 501 | M0 · 1502 |
| P15 | Especificar contratos do Research Agent | Contratos de entrada e saída do Agente 01 | Research Agent | 357, 502 | M0 · 1502 |
| P16 | Definir versionamento, promoção e rollback dos modelos | Versionamento, promoção e rollback | Model Registry | 358, 503 | M0 · 1502 |
| P17 | Estabelecer comportamento do agente sob intervenção manual | Comportamento do agente sob intervenção manual | Trading Agent / Control Manager | 359, 504 | M1 · 1504 |
| P18 | Definir mecanismos de detecção de degradação e gatilhos de retreinamento | Detecção de degradação e retreinamento | Learning Engine | 360, 505 | M3 provisório · 1505 |

## D03

Fonte de domínio: [Domínio 03 - Risco, Execução e Controle Operacional](<../referencias/originais/Domínio 03 - Risco, Execução e Controle Operacional.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P19 | Política quantitativa de risco e limites por mercado | — | Risk Engine | 450, 642 | M0 · 1509 |
| P20 | Cálculo de tamanho, margem, exposição e risco por operação | — | Risk Engine | 451, 643 | M0 · 1509 |
| P21 | Tipos de ordens e filtros específicos Binance Spot/Futures | — | Execution Engine | 452, 644 | M0 · 1509 |
| P22 | Máquina de estados completa e regras de idempotência | — | Execution Engine | 453, 645 | M0 · 1509 |
| P23 | Contratos e frequência de reconciliação | — | Position & Portfolio Manager | 454, 646 | M0 · 1509 |
| P24 | Fórmulas de PnL, taxas, funding e patrimônio | — | Position & Portfolio Manager | 455, 647 | M0 · 1509 |
| P25 | Configuração de margem, alavancagem e One-way Mode | — | Position Manager / Binance Adapter | 456, 648 | M0 · 1509 |
| P26 | Permissões, autenticação e confirmação de intervenções | — | Control Manager | 457, 649 | M0 · 1509 |
| P27 | Regras de aprovação em SUPERVISED e retomada em AUTO | Regras de aprovação em SUPERVISED e retomada AUTO | Control Manager | 458, 650 | M0 · 1509 |
| P28 | Critérios e procedimentos de emergência | — | Risk / Control / Execution | 459, 651 | M0 · 1509 |
| P29 | Recuperação de falhas, timeout e estados incertos | — | Execution Engine | 460, 652 | M1 · 1511 |
| P30 | Estratégia de proteção e encerramento em indisponibilidade | Proteção e encerramento durante indisponibilidade | Risk / Execution | 461, 653 | M1 · 1511 |
| P31 | Contratos de eventos e trilha de auditoria | — | Observability | 462, 654 | M1 · 1511 |
| P32 | Testes de integração, falhas e recuperação operacional | — | QA / Engenharia | 463, 655 | M1 · 1511 |

## D04

Fonte de domínio: [Domínio 04 - Plataforma de Operações e Observabilidade](<../referencias/originais/Domínio 04 - Plataforma de Operações e Observabilidade.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P33 | Arquitetura frontend, framework e organização dos módulos | — | Plataforma | 415, 651 | M0 · 1515 |
| P34 | Especificação OpenAPI e contratos de streaming | — | Operations API | 416, 652 | M0 · 1515 |
| P35 | Modelo de autenticação, RBAC e permissões por ambiente | Autenticação, RBAC e permissões por ambiente | Segurança | 417, 653 | M0 · 1515 |
| P36 | Design System e padrões de UX operacional | — | UI/UX | 418, 654 | M0 · 1515 |
| P37 | Plugins gráficos para SMC, sinais, ordens e proteções | — | Operations Viewer | 419, 655 | M0 · 1515 |
| P38 | Regras de atualização, sequência, reconexão e staleness | Atualização, sequência, reconexão e staleness | BFF / Viewer | 420, 656 | M0 · 1515 |
| P39 | Fluxos de confirmação e proteção contra comandos duplicados | Confirmação e proteção contra comandos duplicados | Manual Console | 421, 657 | M0 · 1515 |
| P40 | Métricas, thresholds, canais e escalonamento de alertas | Métricas, thresholds, canais e escalonamento | Monitoring | 422, 658 | M0 · 1515 |
| P41 | Modelo de incidentes e procedimentos de resposta | Modelo de incidentes e resposta operacional | Monitoring / Operações | 423, 659 | M0 · 1515 |
| P42 | Contratos de replay, ordenação e reconstrução histórica | Contratos de replay e reconstrução histórica | Replay & Analytics | 424, 660 | M1 · 1517 |
| P43 | KPIs operacionais e financeiros e suas definições | KPIs operacionais e financeiros | Analytics | 425, 661 | M1 · 1517 |
| P44 | Retenção, consulta e integridade dos eventos de auditoria | Retenção e integridade de eventos de auditoria | Dados / Segurança | 426, 662 | M1 · 1517 |
| P45 | Segregação técnica entre TRAINING, PAPER e LIVE | Segregação técnica TRAINING, PAPER e LIVE | Plataforma / Segurança | 427, 663 | M2 · 1518 |
| P46 | Requisitos de desempenho, disponibilidade e escalabilidade | Desempenho, disponibilidade e escalabilidade | Engenharia | 428, 664 | M2 · 1518 |
| P47 | Testes E2E, acessibilidade, segurança e falhas de interface | Testes E2E, acessibilidade, segurança e falhas | QA | 429, 665 | M2 · 1518 |

## D05

Fonte de domínio: [Domínio 05 - Plataforma de Dados, Eventos e Auditoria](<../referencias/originais/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P48 | Modelo físico PostgreSQL, schemas, constraints e índices | — | Data Engineering | 536, 795 | M0 · 1522 |
| P49 | Ownership de escrita, transações e limites de consistência | Ownership de escrita, transações e consistência | Arquitetura / Backend | 537, 796 | M0 · 1522 |
| P50 | Modelo de Event Store, Outbox e dispatcher | — | Event Architecture | 538, 797 | M0 · 1522 |
| P51 | Política de ordenação, idempotência, retries e quarentena | Ordenação, idempotência, retries e quarentena | Event Architecture | 539, 798 | M0 · 1522 |
| P52 | Critérios para adoção de broker dedicado | Critérios para broker dedicado | Arquitetura / SRE | 540, 799 | M2 · 1525 |
| P53 | Modelo de armazenamento histórico e particionamento | Armazenamento histórico e particionamento | Data Engineering | 541, 800 | M2 · 1525 |
| P54 | Política de retenção de order book, trades e demais dados volumosos | Retenção de order book, trades e dados volumosos | Market Data | 542, 801 | M2 · 1525 |
| P55 | Regras de temporalidade, disponibilidade e correções históricas | Temporalidade, disponibilidade e correções históricas | Market Data / AI | 543, 802 | M0 · 1522 |
| P56 | Catálogo de features, normalização e versionamento | — | Feature Engineering | 544, 803 | M0 · 1522 |
| P57 | Manifestos de datasets e reprodução de experimentos | — | Learning Engine | 545, 804 | M0 · 1522 |
| P58 | Modelo de correlação e relacionamento entre eventos operacionais | Correlação entre eventos operacionais | Audit & Traceability | 546, 805 | M0 · 1522 |
| P59 | Integridade, retenção e proteção da trilha de auditoria | Integridade e proteção da auditoria | Segurança / Dados | 547, 806 | M1 · 1524 |
| P60 | Read Models, atualização incremental e reconstrução | Read Models e reconstrução | Analytics | 548, 807 | M0 · 1522 |
| P61 | Catálogo de contratos, schema registry e compatibilidade | Catálogo de contratos e compatibilidade | Integração | 549, 808 | M0 · 1522 |
| P62 | Backup, restore, RPO, RTO e testes de recuperação | Backup, restore, RPO, RTO e testes | SRE / Infraestrutura | 550, 809 | M1 · 1524 |
| P63 | Segurança, criptografia e isolamento por ambiente | Segurança, criptografia e isolamento | Segurança | 551, 810 | M0 · 1522 |
| P64 | Capacidade, crescimento, desempenho e observabilidade do banco | Capacidade, crescimento e desempenho | Data Engineering / SRE | 552, 811 | M2 · 1525 |

## D06

Fonte de domínio: [Domínio 06 · Infraestrutura, Segurança e DevOps](<../referencias/originais/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P65 | Seleção do provedor cloud e região de implantação | Seleção do provedor cloud e região | Arquitetura / Infra | 507, 821 | M1 · 1531 |
| P66 | Topologia de rede, VPC, sub-redes, firewall e egress | Topologia de rede, VPC, firewall e egress | Infra / Segurança | 508, 822 | M0 · 1529 |
| P67 | Dimensionamento de CPU, memória, armazenamento e rede | Dimensionamento de recursos computacionais | Infra / SRE | 509, 823 | M1 · 1531 |
| P68 | Escolha da orquestração e política de reinício de containers | Orquestração e reinício de containers | Platform Engineering | 510, 824 | M0 · 1529 |
| P69 | Segregação física/lógica de TRAINING, PAPER e LIVE | Isolamento técnico TRAINING/PAPER/LIVE | Segurança / Infra | 511, 825 | M0 · 1529 |
| P70 | Secrets Manager e proteção das chaves Binance | — | Segurança | 512, 826 | M1 · 1531 |
| P71 | IAM, MFA, RBAC e identidades de serviço | — | Segurança | 513, 827 | M0 · 1529 |
| P72 | Pipeline CI/CD, artefatos e estratégia de promoção | CI/CD, artefatos e promoção entre ambientes | DevOps | 514, 828 | M0 · 1529 |
| P73 | Testes e critérios de aprovação de releases LIVE | Testes e aprovação de releases LIVE | QA / DevOps | 515, 829 | M1 · 1531 |
| P74 | Estratégia de deploy com posições abertas | Deploy com posições abertas | Execution / SRE | 516, 830 | M1 · 1531 |
| P75 | Stack de métricas, logs, traces e alertas | — | Observability | 517, 831 | M0 · 1529 |
| P76 | Definição de SLIs, SLOs e error budgets | SLIs, SLOs e error budgets | SRE | 518, 832 | M1 · 1531 |
| P77 | Política de backup, retenção e restauração | Política de backup e restauração | Data / SRE | 519, 833 | M1 · 1531 |
| P78 | RPO, RTO e arquitetura de Disaster Recovery | RPO, RTO e arquitetura de DR | SRE / Infra | 520, 834 | M1 · 1531 |
| P79 | Runbooks de incidentes e reconciliação pós-falha | Runbooks e reconciliação pós-falha | SRE / Trading | 521, 835 | M1 · 1531 |
| P80 | Hardening, vulnerabilidades e supply chain | Hardening e segurança da supply chain | Segurança | 522, 836 | M1 · 1531 |
| P81 | Infraestrutura como código e controle de drift | — | DevOps | 523, 837 | M1 · 1531 |
| P82 | Contrato OperationalReadiness e critérios de bloqueio | Contrato OperationalReadiness | Arquitetura / Risk | 524, 838 | M0 · 1529 |
| P83 | Custos mensais, capacidade e escalabilidade | Custos, capacidade e escalabilidade | Infra / FinOps | 525, 839 | M2 · 1532 |
| P84 | Testes de resiliência, failover e recuperação | — | QA / SRE | 526, 840 | M1 · 1531 |

## D07

Fonte de domínio: [Domínio 07 - Engenharia, Qualidade e Validação Operacional](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>).

| ID | Descrição de origem | Resumo posterior, quando diferente | Área indicada | Linhas no domínio | Fase · linha Blueprint |
|---|---|---|---|---|---|
| P85 | Organização de repositórios, módulos e padrões de código | Repositórios, módulos e padrões de código | Engineering | 592, 974 | M0 · 1536 |
| P86 | Matriz de rastreabilidade ADR → requisitos → testes | Rastreabilidade ADR → requisito → teste | Arquitetura / QA | 593, 975 | M0 · 1536 |
| P87 | Definition of Done e governança de revisão | Definition of Done e revisão de código | Engineering | 594, 976 | M0 · 1536 |
| P88 | Frameworks e infraestrutura de testes automatizados | Frameworks e infraestrutura de testes | QA | 595, 977 | M0 · 1536 |
| P89 | Catálogo de invariantes financeiros e testes property-based | Invariantes financeiros e property-based testing | QA / Risk | 596, 978 | M0 · 1536 |
| P90 | Testes de contratos entre D01–D06 | Testes de contratos entre domínios | Integração / QA | 597, 979 | M0 · 1536 |
| P91 | Modelagem de custos, fills, slippage e latência no backtest | Custos, fills, slippage e latência no backtest | Quant / Trading | 598, 980 | M0 · 1536 |
| P92 | Simulação de margem, alavancagem e liquidação | Margem, alavancagem e liquidação simulada | Quant / Risk | 599, 981 | M0 · 1536 |
| P93 | Protocolo Walk-forward, embargo e OOS | Protocolo walk-forward, embargo e OOS | AI / Quant | 600, 982 | M0 · 1536 |
| P94 | Benchmarks e análise de robustez estatística | Benchmarks e robustez estatística | AI / Quant | 601, 983 | M0 · 1536 |
| P95 | Reprodutibilidade e registro de experimentos | Reprodutibilidade de experimentos | MLOps | 602, 984 | M0 · 1536 |
| P96 | Paper Execution Adapter e paridade PAPER/LIVE | — | Execution | 603, 985 | M0 · 1536 |
| P97 | Duração e amostra mínima de PAPER | — | Trading / Risk | 604, 986 | M1 · 1538 |
| P98 | Catálogo de falhas e testes de caos | — | QA / SRE | 605, 987 | M0 · 1536 |
| P99 | Testes de reconciliação e recuperação de ordens | Reconciliação e recuperação de ordens | Execution / QA | 606, 988 | M0 · 1536 |
| P100 | Critérios quantitativos por gate | — | Risk / Quant | 607, 989 | M0 · 1536 |
| P101 | Evidências obrigatórias e estrutura do Evidence Bundle | Evidence Bundle e evidências obrigatórias | QA / Governança | 608, 990 | M0 · 1536 |
| P102 | Workflow de aprovação Go/No-Go | — | Governança / Risk | 609, 991 | M1 · 1538 |
| P103 | Política de capital e exposição para LIVE Limited | Capital e exposição para LIVE Limited | Risk / Gestores | 610, 992 | M1 · 1538 |
| P104 | Critérios de suspensão, rollback e retorno a PAPER | Suspensão, rollback e retorno a PAPER | Trading / SRE | 611, 993 | M1 · 1538 |
| P105 | Relatórios de qualidade e indicadores de defeitos | Relatórios de qualidade e defeitos | QA | 612, 994 | M2 · 1539 |
| P106 | Testes integrados de aceitação e homologação LIVE | Testes integrados de homologação LIVE | QA / Operações | 613, 995 | M1 · 1538 |
