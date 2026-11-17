# Reconciliação das ADRs 001 a 098

Registro de governança de 12/11/2026 em `IN_REVIEW`. As decisões ADR-001–088 são as registradas como aprovadas nas fontes de domínio e preservadas na baseline global. TS-ADR-089–098 são aprovadas na seção final do Engineering Foundation. O estado da decisão arquitetural é distinto do estado deste índice. Os números abaixo apontam para linhas das versões TXT recuperadas.

As tabelas citam a decisão registrada. Uma linha de proposta identifica texto anterior útil para rastrear detalhes e não demonstra, por si só, aprovação de todo detalhe omitido na consolidação. A ausência de linha de proposta indica que este índice usa o registro de aprovação como referência por ID. Consulte [divergências e decisões pendentes](RECONCILIATION-DECISIONS.md) para lacunas de contexto, alternativas e consequências.

## D01

Fonte: [Domínio 01 - Integração e Dados de Mercado](<../referencias/originais/Domínio 01 - Integração e Dados de Mercado.txt>). Registro de aprovação na linha 234.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-001 | Separação dos componentes — Market Data, Feature Engine e Market State como componentes lógicos independentes | 240 | — |
| ADR-002 | Escopo inicial — BTCUSDT, Binance Spot e USDⓈ-M Futures | 241 | — |
| ADR-003 | Timeframes — Decisão principal em 5m; contexto em 1m, 15m e 1h | 242 | — |
| ADR-004 | Features — Price Action, Smart Money, volatilidade, volume, order flow e derivativos | 243 | — |
| ADR-005 | Persistência — PostgreSQL inicialmente, com possibilidade de especialização | 244 | — |
| ADR-006 | Trading Observation — Market State separado de Position State, Portfolio State e Risk State | 245 | — |

## D02

Fonte: [Domínio 02 - Inteligência Artificial e Aprendizado](<../referencias/originais/Domínio 02 - Inteligência Artificial e Aprendizado.txt>). Registro de aprovação na linha 418.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-007 | Arquitetura dos agentes — Agente 01, Agente 02 e Learning Engine independentes logicamente | 407 | 273 |
| ADR-008 | Prioridade — Agente 02 implementado primeiro; Agente 01 em evolução posterior | 408 | 280 |
| ADR-009 | Espaço de ações — HOLD, OPEN_LONG, OPEN_SHORT, REDUCE e CLOSE | 409 | 287 |
| ADR-010 | Responsabilidade pelo risco — Agente propõe; políticas independentes controlam exposição, alavancagem e proteção | 410 | 294 |
| ADR-011 | Trading Observation — Observation Builder combina Market, Position, Portfolio e Risk State | 411 | 301 |
| ADR-012 | Trading Environment — Simulador próprio compatível com Gymnasium | 412 | 308 |
| ADR-013 | Modelos de IA — PPO como candidato inicial, com benchmarks de SAC, DQN e estratégias determinísticas | 413 | 315 |
| ADR-014 | Reward Function — Retorno patrimonial líquido com penalidades de risco e turnover | 414 | 322 |
| ADR-015 | Ciclo de aprendizado — Treinamento offline, walk-forward, paper trading e promoção controlada | 415 | 329 |
| ADR-016 | Governança — Treinamento e inferência separados; modelos versionados, aprovados e reversíveis | 416 | 336 |

## D03

Fonte: [Domínio 03 - Risco, Execução e Controle Operacional](<../referencias/originais/Domínio 03 - Risco, Execução e Controle Operacional.txt>). Registro de aprovação na linha 543.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-017 | Arquitetura do domínio — Quatro componentes lógicos independentes: Risk, Execution, Position & Portfolio e Control Manager | 530 | 366 |
| ADR-018 | Autoridade operacional — Intenções automáticas e manuais passam por controle de autoridade e avaliação de risco | 531 | 378 |
| ADR-019 | Políticas de risco — Políticas versionadas em quatro níveis: portfólio, operação, mercado e segurança | 532 | 390 |
| ADR-020 | Dimensionamento e proteção — Risk Engine controla exposição, quantidade, alavancagem e proteção | 533 | 402 |
| ADR-021 | Execução centralizada — Somente Execution Engine encaminha ordens ao Binance Adapter | 534 | 414 |
| ADR-022 | Gestão de posições — Estado financeiro interno reconciliado com a Binance, incluindo ordens pendentes | 535 | 426 |
| ADR-023 | Configuração de Futuros — One-way Mode no MVP; Hedge Mode reservado para evolução | 536 | — |
| ADR-024 | Modos de controle — AUTO, SUPERVISED e MANUAL, com bloqueio de emergência | 537 | — |
| ADR-025 | Intervenção manual — Pausa, redução, fechamento, ajustes de proteção, cancelamento e retomada auditáveis | 538 | — |
| ADR-026 | Circuit breakers — Bloqueio de exposição, cancelamento de ordens de abertura e encerramento controlado | 539 | — |
| ADR-027 | Tratamento de falhas — Fail-safe para entradas, reconciliação e recuperação antes da retomada | 540 | — |
| ADR-028 | Auditoria e observabilidade — Rastreabilidade ponta a ponta das decisões e operações | 541 | — |

## D04

Fonte: [Domínio 04 - Plataforma de Operações e Observabilidade](<../referencias/originais/Domínio 04 - Plataforma de Operações e Observabilidade.txt>). Registro de aprovação na linha 519.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-029 | Arquitetura da plataforma — Cinco módulos funcionais integrados em aplicação web, com separação lógica | 541 | 331 |
| ADR-030 | Operations API / BFF — Fronteira de autenticação, autorização, agregação e streaming; frontend sem credenciais Binance | 542 | 343 |
| ADR-031 | Admin & Operations Portal — Administração centralizada de ambientes, contas, agentes, modelos, políticas e usuários | 543 | 355 |
| ADR-032 | Biblioteca de gráficos — TradingView Lightweight Charts no MVP, com extensões para sinais, SMC, ordens e proteções | 544 | 367 |
| ADR-033 | Operations Viewer — Visualização distinta de decisões da IA, autorizações de risco e execuções | 545 | 379 |
| ADR-034 | Manual Trading Console — Intervenções encaminhadas por Control Manager, Risk Engine e Execution Engine | 546 | 391 |
| ADR-035 | Atualização em tempo real — Snapshot inicial e eventos incrementais via WebSocket/SSE, com recuperação | 547 | — |
| ADR-036 | Monitoring & Alerts — Monitoramento operacional e gestão de alertas classificados por severidade | 548 | — |
| ADR-037 | Strategy Replay & Analytics — Replay factual e analytics básicos no MVP; análises contrafactuais posteriormente | 549 | — |
| ADR-038 | Segurança e permissões — RBAC, menor privilégio, segregação de funções e confirmação reforçada | 550 | — |
| ADR-039 | Segregação de ambientes — Separação explícita entre TRAINING, PAPER e LIVE | 551 | — |
| ADR-040 | Governança da interface — Qualidade e atualização dos dados, auditoria humana e confirmação efetiva das operações | 552 | — |

## D05

Fonte: [Domínio 05 - Plataforma de Dados, Eventos e Auditoria](<../referencias/originais/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt>). Registro de aprovação na linha 637.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-041 | Arquitetura com seis componentes lógicos independentes | 656 | 440 |
| ADR-042 | PostgreSQL como banco principal do MVP, com schemas e ownership | 657 | 452 |
| ADR-043 | Separação conceitual entre Event Store e Event Bus | 658 | 464 |
| ADR-044 | Transactional Outbox, entrega at-least-once e idempotência | 659 | 476 |
| ADR-045 | PostgreSQL Outbox com dispatcher persistente no MVP | 660 | 488 |
| ADR-046 | Histórico de mercado com qualidade, origem e retenção | 661 | 500 |
| ADR-047 | Temporalidade `event_time`, `received_at`, `available_at` | 662 | 512 |
| ADR-048 | Versionamento de features, observações e datasets | 663 | — |
| ADR-049 | Rastreabilidade ponta a ponta das operações | 664 | — |
| ADR-050 | Auditoria append-only e verificações de integridade | 665 | — |
| ADR-051 | Read Models e CQRS leve, sem Event Sourcing integral obrigatório | 666 | — |
| ADR-052 | Contratos de eventos padronizados e versionados | 667 | — |
| ADR-053 | Estados autoritativos para decisões financeiras críticas | 668 | — |
| ADR-054 | Governança, segurança, retenção, backup e recuperação | 669 | — |

## D06

Fonte: [Domínio 06 · Infraestrutura, Segurança e DevOps](<../referencias/originais/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>). Registro de aprovação na linha 623.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-055 | Arquitetura do domínio com seis componentes lógicos | 642 | 401 |
| ADR-056 | Infraestrutura cloud; provedor a selecionar | 643 | 413 |
| ADR-057 | Containers OCI/Docker; sem Kubernetes obrigatório no MVP | 644 | 425 |
| ADR-058 | Segregação de TRAINING, PAPER e LIVE | 645 | 437 |
| ADR-059 | Proteção de credenciais Binance e acesso restrito | 646 | 449 |
| ADR-060 | IAM, MFA, RBAC e menor privilégio | 647 | 461 |
| ADR-061 | CI/CD com testes, segurança e artefatos versionados | 648 | 473 |
| ADR-062 | Aprovação reforçada para releases críticos LIVE | 649 | 485 |
| ADR-063 | Proteção de posições durante deploys | 650 | — |
| ADR-064 | Observabilidade técnica e correlação operacional | 651 | — |
| ADR-065 | SLIs, SLOs e error budgets por criticidade | 652 | — |
| ADR-066 | Backup, Disaster Recovery e recuperação testada | 653 | — |
| ADR-067 | Reconciliação financeira antes da retomada | 654 | — |
| ADR-068 | Hardening, criptografia e segurança da supply chain | 655 | — |
| ADR-069 | Infraestrutura como código e controle de drift | 656 | — |
| ADR-070 | OperationalReadiness obrigatório para LIVE | 657 | — |

## D07

Fonte: [Domínio 07 - Engenharia, Qualidade e Validação Operacional](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>). Registro de aprovação na linha 744.

| ADR | Decisão registrada | Linha da decisão | Linha de proposta localizada |
|---|---|---|---|
| ADR-071 | Arquitetura do domínio com seis componentes lógicos | 766 | 472 |
| ADR-072 | Governança de engenharia e rastreabilidade das entregas | 767 | 484 |
| ADR-073 | Estratégia multicamadas de testes automatizados | 768 | 496 |
| ADR-074 | Invariantes financeiros como bloqueios de promoção | 769 | 508 |
| ADR-075 | Backtesting realista com custos e restrições | 770 | 520 |
| ADR-076 | Walk-forward e validação fora da amostra | 771 | 532 |
| ADR-077 | Benchmarks e análise de robustez | 772 | 544 |
| ADR-078 | Reprodutibilidade de experimentos | 773 | 556 |
| ADR-079 | Paper Trading obrigatório antes de LIVE | 774 | 568 |
| ADR-080 | Paridade lógica entre PAPER e LIVE | 775 | — |
| ADR-081 | Testes de resiliência e recuperação | 776 | — |
| ADR-082 | Gates progressivos G0–G5 | 777 | — |
| ADR-083 | Critérios quantitativos de aceite | 778 | — |
| ADR-084 | Revalidação após alterações materiais | 779 | — |
| ADR-085 | Liberação LIVE com capital e exposição limitados | 780 | — |
| ADR-086 | Suspensão e retorno a PAPER | 781 | — |
| ADR-087 | Evidence Bundle e auditoria das aprovações | 782 | — |
| ADR-088 | Separação de responsabilidades entre domínios | 783 | — |

## Decisões técnicas I00

Fonte: [TS-ENG-I00-V1.0 - Engineering Foundation](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>). A aprovação final de T01–T10 e TS-ADR-089–098 consta nas linhas 824–855. As propostas anteriores são mantidas como histórico. TS-ADR-093 tem ficha de referência nas linhas 634–646 com contexto, decisão, consequências e alternativas. A ficha conserva o estado histórico `PROPOSED`. A aprovação da decisão consta no registro posterior.

| ADR | Decisão aprovada | Linha aprovada | Linhas de proposta |
|---|---|---|---|
| TS-ADR-089 | Python como linguagem principal do backend e IA | 844 | 189, 621 |
| TS-ADR-090 | Monorepo modular com isolamento seletivo de processos | 845 | 190, 622 |
| TS-ADR-091 | FastAPI e Pydantic v2 | 846 | 191, 623 |
| TS-ADR-092 | PostgreSQL, SQLAlchemy 2 e Alembic | 847 | 192, 624 |
| TS-ADR-093 | Transactional Outbox e consumidores idempotentes | 848 | 193, 625, 634–646 |
| TS-ADR-094 | uv, Ruff, mypy, pytest e Hypothesis | 849 | 194, 626 |
| TS-ADR-095 | Docker Compose e GitHub Actions | 850 | 195, 627 |
| TS-ADR-096 | OpenTelemetry e logs estruturados | 851 | 196, 628 |
| TS-ADR-097 | JSON Schema, OpenAPI e contratos versionados | 852 | 197, 629 |
| TS-ADR-098 | Segurança fail-closed e LIVE indisponível no I00 | 853 | 198, 630 |
