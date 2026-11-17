# Rastreabilidade DOC-03 para o Trading Core PAPER

Registro de 12/11/2026 em `IN_REVIEW`. O Blueprint vincula TS-EP-05 a P19–P32 e TS-EP-06 a P19–P32, P96 e P99 no catálogo de épicos. TS-ST-009–012 e seus critérios constam nas linhas 2027–2030. Os vínculos abaixo por história, ADR, componente e verificação foram inferidos por conteúdo e aguardam revisão. Os resultados históricos descrevem os ensaios de 11/11. A execução unitária registrada abaixo cobre o simulador Spot inicial na cópia anterior. A conferência no checkout oficial localizou também os caminhos integrados de Market State em PAPER.

- [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)
- [Pendências por ID](PENDING-ITEM-RECONCILIATION.md) · [ADRs por ID](ADR-RECONCILIATION.md) · [Market State de I02](DOC-03-I01-I02-TRACEABILITY.md)
- [Especificação de Control e Risk](../domains/d03-control-risk-paper.md)
- [Especificação de execução simulada e reconciliação do Portfolio](../domains/d03-execution-portfolio-paper.md)

## Histórias, contratos e verificações

| História e critério | Componente e artefatos | Pendências e ADRs relacionadas | Verificação e limite |
|---|---|---|---|
| TS-ST-009 · TS-EP-05 · modos e emergency lock testados | D03-C04 · TradingIntent e ControlPolicy | P26–P28 · ADR-017, ADR-018, ADR-024–026 | `test_control_blocks_non_paper_before_risk` e `test_control_rejections_preserve_balance` cobrem ambiente, pausa, conta, ator e validade. O ensaio com Market State registra bloqueio antes de ler o estado para uma intenção LIVE. Transições de modo, confirmações humanas e ciclo do emergency lock seguem abertos. [Testes](../../tests/unit/test_paper_simulator.py) · [Market State em PAPER](../evidence/I03-market-state-paper.md) |
| TS-ST-010 · TS-EP-05 · APPROVED, ADJUSTED e REJECTED com invariantes | D03-C01 · RiskLimits, cotação e saldo PAPER | P19, P20, P25, P28 · ADR-019, ADR-020, ADR-023, ADR-026, ADR-074 | `test_risk_rejections_preserve_balance` cobre limites nocional e de posição, insuficiência de saldo e posição, cotação vencida e quantidade inválida. As evidências históricas acrescentam custo total, colateral e margem isolada a 1×. Falta evidência de decisão ADJUSTED, sizing e políticas versionadas por mercado. [Testes](../../tests/unit/test_paper_simulator.py) · [Custos](../evidence/I03-custos-paper.md) · [Futures](../evidence/I03-futures-paper.md) |
| TS-ST-011 · TS-EP-06 · ordens e fills simulados e idempotentes | D03-C02 · PaperSimulator, PaperFill e chave por conta e intenção no livro-razão | P21, P22, P29–P32, P96, P99 · ADR-018, ADR-021, ADR-027, ADR-028, ADR-079–081 | `test_paper_buy_sell_and_replay_use_exact_balances` cobre compra, venda, replay e conflito de conteúdo no simulador em memória. A evidência histórica cobre replay entre processos, rollback, conflito de fechamento e vínculo ao Market State. A máquina de ordens, filtros, tratamento de timeout e estados incertos e paridade com execução externa seguem sem evidência neste recorte. [Testes](../../tests/unit/test_paper_simulator.py) · [Livro-razão](../evidence/I03-persistencia-paper.md) · [Market State em PAPER](../evidence/I03-market-state-paper.md) |
| TS-ST-012 · TS-EP-06 · posição, equity e PnL consistentes | D03-C03 e D05-C01 · saldos, posição, margem, PnL e reconciliação do livro-razão | P23–P25, P29, P31, P32, P99 · ADR-022, ADR-023, ADR-027, ADR-028, ADR-053, ADR-074 | O teste unitário de compra/venda verifica saldos decimais. Os ensaios históricos cobrem recomposição do saldo e posição, detecção de divergência, taxas e slippage Spot e PnL realizado em Futures long/short a 1×. Equity completa, funding, liquidação e periodicidade de reconciliação seguem abertos. A recomposição local cobre fills simulados. [Testes](../../tests/unit/test_paper_simulator.py) · [Livro-razão](../evidence/I03-persistencia-paper.md) · [Custos](../evidence/I03-custos-paper.md) · [Futures](../evidence/I03-futures-paper.md) |

## Decisões e fontes ainda necessárias

| Pendências | O que precisa de decisão, fonte ou evidência |
|---|---|
| P19, P20, P24, P25 | Aprovar política quantitativa por mercado e especificar dimensionamento, critérios de ajuste, equity, funding e limites de margem. Taxas, slippage e limites sintéticos dos ensaios não estabelecem valores normativos. |
| P26–P28 e P30 | Formalizar a autoridade por modo, a aprovação em SUPERVISED, a retomada e os cenários de emergência e indisponibilidade. Identificar quais proteções são essenciais para PAPER e quais testes devem demonstrá-las. |
| P21, P22, P29 e P96 | Especificar filtros e tipos aplicáveis ao simulador, estados de ordem e comportamento diante de reenvio, timeout e estados incertos. Definir critérios de paridade lógica e verificá-los com contratos e simulações autorizadas. |
| P23, P31, P32 e P99 | Definir contratos de reconciliação e auditoria, cadência, responsáveis e testes de falha e recuperação. A evidência histórica cobre divergências do livro-razão e rollback local. P29–P32 mantêm M1. Qualquer antecipação de proteções essenciais para PAPER segue G40. |
| Identidade e aceite do candidato | Localizar snapshot ou commit de I03 com suítes de integração e resultados vinculados às migrations 0008–0011. As notas de 11/11 documentam ensaios e contagens, sem identificar nessas notas um commit candidato comum ou aceite humano consolidado de I03. Registrar eventual decisão existente e seu escopo. |

## Evidência de integração localizada no checkout oficial

`PaperLedger.submit_with_quote_provider` e o método correspondente em `PaperFuturesLedger` estão presentes. A suíte de PostgreSQL contém `test_paper_market_state_obeys_decision_cutoff_and_preserves_evidence` e `test_futures_market_state_cutoff_and_reconciliation`. Permanecem pendentes a execução integrada rastreável, a vinculação ao candidato e o aceite de I03. [Suíte de integração](../../tests/integration/test_postgres_migrations.py)

## Verificação histórica e conferência no checkout oficial

`python -m pytest -p no:cacheprovider tests/unit/test_paper_simulator.py --tb=short` executado com a venv do projeto em 12/11/2026. **14 testes passaram**. A suíte exercita o simulador Spot em memória. Os ensaios de persistência, Market State, custos e Futures permanecem referenciados como evidência histórica de PostgreSQL. A verificação atual não inclui execução dessas integrações. DOC-03 permanece parcial e G0 segue aberto.
