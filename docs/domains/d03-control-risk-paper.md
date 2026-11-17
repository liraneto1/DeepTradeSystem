# Especificação de Control e Risk do Trading Core PAPER

**D03 · I03 · DRAFT · 12/11/2026**

Esta especificação detalha D03-C04 (Control Manager) e D03-C01 (Risk Engine) para TS-ST-009 e TS-ST-010. As regras conceituais vêm de D03 e do Blueprint. Os comportamentos do simulador Spot e os ensaios históricos identificam a cobertura disponível. O registro de decisões ao final indica o que precisa ser validado para transformar essa cobertura em critérios de aceite de I03. O recorte usa BTCUSDT, contas simuladas e ambiente PAPER. LIVE permanece indisponível.

- [D03 original em texto, seções 5, 8, 9 e baseline conceitual](<../referencias/originais/Domínio 03 - Risco, Execução e Controle Operacional.txt>)
- [Blueprint, fluxos F03, F06 e F10](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)
- [Visão de arquitetura](../architecture/trading-core-paper.md) · [Matriz I03](../governance/DOC-03-I03-TRACEABILITY.md)

## Fronteira de autorização

1. Control recebe uma `TradingIntent` e avalia a autoridade para conta, ator, ambiente e instante. Intenções automáticas e manuais passam pelo mesmo encadeamento de autorização.
2. Risk avalia a intenção autorizada usando cotação ou Market State, posição, saldo e política aplicável. Execution só recebe intenção apta após Control e Risk. Toda operação que aumenta exposição exige autorização de risco válida.
3. Se houver rejeição, nenhuma nova execução simulada ou mutação de saldo e posição pode resultar da tentativa. Uma operação de proteção pode ter procedimento de emergência próprio, com verificação de identidade, autoridade, consistência e segurança.
4. Falha de comunicação ou estado inconsistente bloqueia novas entradas no escopo afetado. Uma ordem com resultado desconhecido exige reconciliação antes de reenvio. Retomada exige validar autoridade, integridade dos dados e reconciliação financeira.

Origem: ADR-017/018, ADR-020, ADR-025–028, F03, F06 e F10. Execution e Portfolio mantêm a responsabilidade pelo fill, pelo estado financeiro e pela reconciliação. Control e Risk usam os resultados dessa reconciliação ao avaliar retomada.

## Control Manager

| Regra | Comportamento do recorte Spot no checkout | Fonte ou verificação |
|---|---|---|
| Ambiente e escopo | Exige `PAPER`. A conta precisa corresponder à política e o ator deve estar na lista autorizada. | ADR-018, P26 · `test_control_blocks_non_paper_before_risk`, `test_control_rejections_preserve_balance` |
| Pausa | A política local começa pausada por padrão. Uma intenção submetida enquanto pausada é rejeitada. | ADR-024/025, P27/P28 · `test_control_rejections_preserve_balance` |
| Identidade da intenção | Exige IDs de intenção e correlação preenchidos, BTCUSDT e ação `BUY` ou `SELL`. | Implementação do recorte Spot em [Control](../../src/trade_system/control/paper.py) |
| Validade | Exige timestamps com fuso e aplica a janela `issued_at ≤ now < expires_at`. Os registros transacionais usam UTC. | P26 · `test_control_rejections_preserve_balance` cobre expiração |
| Limite de autoridade | Uma rejeição em Control impede a avaliação de Risk no caminho observado pelo teste de ambiente. A evidência histórica com Market State registra rejeição antes de ler a cotação para uma intenção LIVE. | ADR-018 · [Ensaio histórico](../evidence/I03-market-state-paper.md) |

D03 prevê `AUTO` para propostas automáticas sujeitas a Risk, `SUPERVISED` com aprovação humana para operações selecionadas e `MANUAL` com autoridade do operador. O Blueprint inclui `PAUSED` e o bloqueio de emergência. Emergency lock bloqueia novas exposições e aciona procedimentos de proteção. A pausa local é um booleano que bloqueia as submissões do simulador. A tabela de transições, a classificação formal de pausa e emergency lock e as exceções para redução de risco seguem pendentes em P26–P28 e P30.

## Risk Engine

D03 organiza políticas versionadas em quatro níveis. A precedência entre níveis e os parâmetros por mercado precisam ser definidos em P19/P20.

| Nível | Escopo definido em D03 | Cobertura disponível |
|---|---|---|
| Capital e portfólio | Patrimônio, exposição, concentração e perdas acumuladas | O simulador verifica saldo, posição disponível e limite de quantidade após compra. |
| Operação individual | Quantidade, risco por operação, alavancagem e proteção | O simulador valida quantidade e nocional. Ensaios históricos acrescentam custos Spot e margem isolada a 1× em Futures. |
| Condições de mercado | Spread, liquidez, volatilidade, funding e qualidade dos dados | O simulador valida preço e idade da cotação. O ensaio de Market State exercita corte de disponibilidade e cotação vencida. |
| Segurança operacional | Drawdown, falhas, divergências e circuit breakers | A baseline exige bloqueio e retomada controlada. Os testes Spot atuais não demonstram gatilhos de drawdown ou circuit breakers. |

### Regras observadas no Spot inicial

- Quantidade, preço e limites de nocional e posição são decimais finitos e positivos. Caixa e quantidade em carteira devem ser finitos e não negativos.
- A cotação precisa ter referência preenchida, símbolo compatível e timestamp com fuso. O intervalo permitido de idade vai de zero até `max_quote_age`, inclusive, com limite de idade positivo.
- O nocional é a quantidade multiplicada pelo preço. Se exceder o limite configurado, Risk rejeita. Uma compra também exige caixa suficiente e posição resultante dentro do limite. Uma venda exige quantidade disponível e preserva posição não negativa.
- No simulador inicial, uma aprovação retorna o nocional e o saldo projetado. As rejeições são expressas por erros de domínio. D03 prevê o contrato conceitual `RiskDecision` com `APPROVED` para operação dentro dos limites, `ADJUSTED` para ajuste de quantidade ou proteção e `REJECTED` para bloqueio. A política de ajuste e o contrato versionado continuam abertos.

O cálculo atual está em [Risk Spot](../../src/trade_system/risk/paper.py). O [teste de rejeições](../../tests/unit/test_paper_simulator.py) cobre limite de nocional, limite de posição, caixa e quantidade insuficientes, cotação vencida e quantidade inválida. Validações descritas apenas pela leitura do código ainda precisam de testes próprios quando integrarem o aceite.

### Extensões com evidência histórica

- **Custos Spot.** O ensaio registra rejeição quando o nocional com slippage excede o limite ou quando o caixa não cobre o custo total. Os parâmetros do ensaio são sintéticos. [Evidência de custos](../evidence/I03-custos-paper.md)
- **Futures.** O ensaio usa uma posição sintética linear USDⓈ-M, margem isolada a 1×, abertura long ou short e fechamento integral. Exercita colateral insuficiente e rejeição de fechamento parcial. ADR-023 define One-way Mode no MVP. P25 ainda requer política de margem e alavancagem para o recorte aplicável. [Evidência de Futures](../evidence/I03-futures-paper.md)

## Contratos e auditoria

O Blueprint identifica `ControlDecision`, `ControlStateEvent`, `RiskDecision` e `RiskLimitEvent` como interfaces lógicas. O D03 prevê registrar política aplicada, limites avaliados e justificativa da avaliação de Risk. ADR-025/028 exigem rastreabilidade das intervenções e decisões. A especificação de schemas, versionamento e publicação pertence a P31.

Para revisão do contrato, registrar por decisão o vínculo à intenção, IDs de conta e correlação, ambiente, timestamp UTC, resultado e motivo. Para Risk, incluir a versão de política, limites avaliados e referência da cotação ou estado usado. Para ajuste, preservar a intenção de origem e o resultado efetivamente autorizado. Esses campos são uma proposta de detalhamento e precisam de validação antes da publicação de schemas.

## Decisões e evidências pendentes

| Referência | Decisão ou fonte necessária | Evidência de aceite esperada |
|---|---|---|
| P26/P27 · TS-ST-009 | Aprovar tabela de autoridade por modo, identidade e permissões, operações que exigem confirmação humana, validade da confirmação e transições de retomada. | Testes por ator, ação e modo, incluindo confirmação inválida, expirada ou reutilizada. |
| P28–P30 · TS-ST-009/010 | Aprovar gatilhos, alcance e liberação do emergency lock, proteções durante pausa ou indisponibilidade e condições de retomada. | Simular bloqueio de nova exposição, redução autorizada, perda de dados e retomada após reconciliação. |
| P19/P20 · TS-ST-010 | Aprovar parâmetros e precedência por nível e mercado, regra de sizing, critérios para `ADJUSTED` e necessidade de confirmação ou nova avaliação após ajuste. | Casos nos limites, ajustes válidos e inválidos, ausência de política e proteção contra execução sem decisão válida. |
| P24/P25 · TS-ST-010/012 | Identificar a fonte normativa de custos, margem, alavancagem, funding e equity e aprovar a parte exigida em PAPER. | Invariantes com parâmetros versionados, colateral e exposição pós-operação. |
| P08/P55 e P19 · TS-ST-010 | Definir fontes aceitas, corte temporal, limite de frescor e tratamento de Market State indisponível. | Testes com cotação futura, atrasada, vencida, indisponível e evidência de linhagem. |
| P31/P32 · F09/F10 | Aprovar schemas, razões de rejeição, correlação, política de retenção e cenários de falha. Recuperar o candidato histórico para verificar as integrações. | Contratos versionados, testes de integração e resultados associados ao commit candidato. |

As fases primárias seguem a baseline. Eventual antecipação de partes críticas de P29–P32 para PAPER segue G40. G0 permanece aberto.

## Evidência disponível

A matriz de I03 registra os 14 testes unitários Spot e os ensaios históricos em PostgreSQL. O caminho integrado de Market State precisa de confirmação no candidato correspondente. No checkout oficial, a entrada chama `submit_with_quote_provider`, presente no `PaperLedger`. A suíte PostgreSQL inclui testes de corte temporal e reconciliação. [Matriz I03](../governance/DOC-03-I03-TRACEABILITY.md) · [Visão de arquitetura](../architecture/trading-core-paper.md)
