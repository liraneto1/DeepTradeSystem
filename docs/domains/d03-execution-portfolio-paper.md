# Especificação de execução simulada e reconciliação do Portfolio PAPER

**D03 · I03 · DRAFT · 12/11/2026**

Esta especificação cobre D03-C02 (Execution Engine) e D03-C03 (Position & Portfolio Manager) para TS-ST-011 e TS-ST-012. O recorte é BTCUSDT em PAPER, com contas, ordens e fills simulados. O PostgreSQL mantém o estado financeiro do livro-razão persistido. A reconciliação descrita aqui compara o estado interno com os próprios fills do simulador. LIVE permanece indisponível.

- [D03 original, seções 6, 7 e 9 e decisões consolidadas](<../referencias/originais/Domínio 03 - Risco, Execução e Controle Operacional.txt>)
- [Visão de arquitetura](../architecture/trading-core-paper.md) · [Matriz I03](../governance/DOC-03-I03-TRACEABILITY.md) · [Especificação de Control e Risk](d03-control-risk-paper.md)

## Execução simulada

| Regra | Comportamento e evidência | Rastreabilidade |
|---|---|---|
| Autorização | O fluxo segue `TradingIntent → Control → Risk → Execution`. Uma rejeição em Control ou Risk não pode criar novo fill nem alterar caixa ou posição. | ADR-017/018/021 · TS-ST-011 |
| Preço e origem | O Spot inicial usa cotação sintética e fill integral. O ensaio histórico com Market State usa o fechamento de 5m disponível na emissão da intenção, valida o frescor na execução e registra referência, linhagem e SHA-256. | P21/P31 · [Market State em PAPER](../evidence/I03-market-state-paper.md) |
| Identidade do fill | Preservar vínculo com a intenção, conta, correlação, cotação, instante UTC, preço, quantidade, nocional e estado financeiro resultante. O modelo usa aritmética decimal. Os campos persistidos variam conforme o recorte. | ADR-028 · P22/P31 · [Simulação inicial](../runbooks/paper-simulacao-inicial.md) |
| Idempotência | No caminho persistido, a chave é conta e ID da intenção. Um replay idêntico dentro da validade exercitada retorna o fill persistido sem novo efeito. Conteúdo conflitante para a mesma chave é recusado. O ensaio com Market State também registra conflito ao mudar o fechamento. | ADR-027 · P22/P29 · [Livro-razão](../evidence/I03-persistencia-paper.md) |
| Atomicidade | O código do livro-razão abre transação e bloqueia a linha da conta ao verificar replay, avaliar o saldo e gravar o fill e o novo estado financeiro. O ensaio de falha após inserir o fill registra rollback integral. | ADR-022/027/053 · P29/P32 · [Implementação Spot](../../infrastructure/database/paper_ledger.py) |
| Resultado incerto | A regra conceitual de D03 exige reconciliar o resultado antes de reenviar. O tratamento no simulador depende da máquina de estados e da política de recuperação de P22/P29. | ADR-027 · P22/P29/P30 |

O D03 original propõe estados como `CREATED`, `SUBMITTING`, `OPEN`, `PARTIALLY_FILLED`, `FILLED` e `UNKNOWN / RECONCILIATION_REQUIRED`. A seleção de estados, transições, filtros e tipos de ordem aplicáveis a PAPER continua em validação. O simulador inicial comprova fill integral e replay no escopo exercitado.

## Estado do Portfolio e reconciliação

| Recorte | Estado e verificação | Limite da evidência |
|---|---|---|
| Spot inicial | Caixa e quantidade partem do saldo de abertura. A reconciliação percorre fills por sequência, recalcula nocional e saldo após cada fill, compara com os registros e aponta a primeira intenção divergente quando identificável. Também compara o saldo final recomposto com o persistido. | A carteira Spot em memória cobre compra e venda com precisão decimal. O replay persistido entre processos e a divergência induzida são resultados históricos. [Evidência](../evidence/I03-persistencia-paper.md) |
| Spot com custos | O ensaio histórico considera slippage e taxa no custo do fill. O replay preserva o fill original e a recomposição detecta taxa persistida divergente. | As taxas e o slippage são parâmetros de teste. O ensaio não estabelece política de custos nem fórmula completa de equity. [Evidência](../evidence/I03-custos-paper.md) |
| Futures PAPER | O recorte sintético usa uma posição linear USDⓈ-M, margem isolada a 1× e abertura long ou short com fechamento integral. A recomposição parte do caixa de abertura e reaplica preço de referência, quantidade e custos registrados para verificar saldo, posição, margem e PnL realizado. | ADR-023 define One-way Mode no MVP. O ensaio não cobre fechamento parcial, funding, liquidação ou uma política geral de alavancagem. [Evidência](../evidence/I03-futures-paper.md) · [Implementação](../../infrastructure/database/paper_futures.py) |

ADR-022/027/028 e F05/F10 orientam a sequência após divergência: registrar a diferença, bloquear novas entradas no escopo afetado, reconciliar os registros e retomar após validação de consistência e autoridade. Os ensaios disponíveis demonstram detecção e recomposição. O contrato de bloqueio, o procedimento de correção auditável e as condições de retomada ainda exigem validação.

## Contratos e auditoria

O Blueprint identifica `OrderCommandResult`, `OrderEvent`, `FillEvent`, `PositionSnapshot`, `PortfolioSnapshot` e `ReconciliationStatus` como interfaces lógicas. O checkout contém tipos internos como `PaperFill`, `Reconciliation` e `FuturesReconciliation`. A publicação dos schemas e eventos de I03 depende de P23/P31.

Como proposta para revisão, um resultado de reconciliação deve identificar conta, mercado, intervalo ou sequência examinada, saldo recomposto, saldo registrado e primeira divergência conhecida. Uma correção deve ter vínculo com a divergência, motivo, ator autorizado e evidência da nova verificação. As versões dos contratos, a retenção e os critérios de resolução aguardam validação.

## Decisões e evidências pendentes

| Referência | Decisão ou fonte necessária | Evidência de aceite esperada |
|---|---|---|
| P21/P22/P96 · TS-ST-011 | Aprovar tipos de ordem, filtros, arredondamento, estados e semântica de preenchimento aplicáveis em PAPER. Definir critérios de paridade lógica por contrato. | Casos de transição, filtro inválido, preenchimento e cancelamento conforme escopo aprovado. |
| P22/P29/P32 · TS-ST-011 | Definir escopo e retenção da chave, identidade de reenvio, tratamento após expiração e política de timeout e resultado incerto. | Replay concorrente e após reinício, conflito sem mutação, rollback e recuperação sem duplicar fill ou efeito financeiro. |
| P23/P30/P99 · TS-ST-012 | Aprovar cadência, gatilhos, tolerâncias, escopo de bloqueio, responsável pela correção e condições de retomada após divergência. | Divergência em fill e saldo final, bloqueio de nova exposição, correção auditável e reconciliação antes da retomada. |
| P24/P25 · TS-ST-012 | Identificar fonte normativa para taxas, slippage, PnL, equity, funding, margem e liquidação. Confirmar quais regras entram no recorte Futures PAPER. | Reprocessamento com parâmetros versionados e invariantes de caixa, posição, margem e PnL. |
| P31 · TS-ST-011/012 | Aprovar schemas, versões, correlação e política de publicação dos eventos de execução, Portfolio e reconciliação. | Contratos verificáveis e rastreamento de intenção, autorização, fill e resultado de reconciliação. |
| Candidato I03 · DOC-03 | Recuperar o commit ou snapshot das migrations 0008–0011 com os testes de integração e os resultados correspondentes. | Execução reproduzível para persistência, Market State, custos e Futures. |

As fases primárias permanecem conforme a baseline. A antecipação de partes críticas de P29–P32 para PAPER segue G40. G0 permanece aberto.

## Evidência e limites do checkout

Os testes unitários Spot exercitam compra, venda, saldos decimais, replay, conflito de conteúdo e preservação do saldo após rejeição. Persistência, custos, reconciliação e Futures usam os resultados históricos vinculados na matriz I03. O fluxo integrado com Market State ainda precisa ser confirmado no candidato histórico. O checkout oficial contém `submit_with_quote_provider` nos livros-razão Spot e Futures e testes de integração de corte temporal e reconciliação. [Testes Spot](../../tests/unit/test_paper_simulator.py) · [Matriz I03](../governance/DOC-03-I03-TRACEABILITY.md)
