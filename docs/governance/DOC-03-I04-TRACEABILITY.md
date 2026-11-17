# Rastreabilidade DOC-03 para I04

Registro de 12/11/2026 em `IN_REVIEW`. O Blueprint, roadmap, ficha do épico e linhas 2031–2032, associa I04 a TS-EP-07, com Observation Builder, PPO, action masks, Model Registry e inferência. TS-ST-013 exige um snapshot determinístico e versionado. TS-ST-014 exige um modelo reproduzível e rastreável. TS-EP-07 cita P09–P18 e depende das features de I02, dos datasets e dos contratos PAPER de TS-EP-06. P56 e P57 aparecem explicitamente em TS-EP-02. Sua atribuição às histórias de I04 é uma proposta de refinamento. Os vínculos abaixo por requisito, componente e verificação foram inferidos por conteúdo.

- [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) · [D02 original](<../referencias/originais/Domínio 02 - Inteligência Artificial e Aprendizado.txt>)
- [Pendências por ID](PENDING-ITEM-RECONCILIATION.md) · [ADRs por ID](ADR-RECONCILIATION.md) · [I01 e I02](DOC-03-I01-I02-TRACEABILITY.md) · [I03](DOC-03-I03-TRACEABILITY.md)

## Histórias, contratos e evidências

| História e recorte | Componentes e interfaces lógicas | Pendências e ADRs | Evidência disponível e limite |
|---|---|---|---|
| TS-ST-013 · Observation Builder | D02-C02, D01-C03, D03 e D05-C04 · Trading Observation derivada de Market, Position, Portfolio e Risk State | P07/P08/P09/P56 · ADR-006/011/047/048 | No checkout oficial, `test_versioned_features_and_lineage`, `test_rejects_late_candles_and_gaps` e `test_multi_interval_uses_only_aligned_and_available_candles` cobrem parte da entrada de mercado. Falta prova de composição determinística dos quatro estados, versão da observação e compatibilidade com o modelo. [Testes de Market State](../../tests/unit/test_market_state.py) · [Ensaio multi-intervalo](../evidence/I02-market-state-multi-intervalo.md) |
| TS-ST-014 · Ambiente de treinamento e PPO | D02-C03 e D05-C04 · Trading Environment, TrainingRun, ModelCandidate, DatasetManifest | P10–P14, P56/P57 · ADR-009/010/012–015/048/078 | Os ensaios de I03 dão referência de saldos, custos e rejeições para cenários do ambiente. O checkout oficial não apresentou evidência de ambiente Gymnasium, execução de treino PPO, artefato de modelo, reward validada ou reprodução com dataset congelado. [Custos PAPER](../evidence/I03-custos-paper.md) · [Futures PAPER](../evidence/I03-futures-paper.md) |
| TS-ST-014 · Model Registry | D02-C03 e D02-C02 · ModelCandidate, ModelEvaluation e referência ao artefato selecionado para inferência | P14/P16/P57 · ADR-015/016/048/078/087 | D02 define versionamento, promoção controlada e rollback. Não foi localizado registro de candidato com lineage de treino, avaliação, hash, aprovação ou ensaio de rollback. O aceite deve demonstrar vínculo do artefato ao treino, ao dataset e às versões de features e observação. [D02 original](<../referencias/originais/Domínio 02 - Inteligência Artificial e Aprendizado.txt>) |
| Inferência e action masks · desdobramento proposto de TS-ST-014 | D02-C02 e D03-C04/C01 · TradingDecision e TradingIntent em F02/F03 | P10/P16/P17 · ADR-007–011/016/018 | I03 documenta Control e Risk após a intenção. Falta evidência de inferência vinculada ao modelo e à observação, máscaras de ações e comportamento sob intervenção manual. A máscara restringe propostas. Toda intenção passa por Control e Risk. [Control e Risk](../domains/d03-control-risk-paper.md) |

P15 trata dos contratos do Research Agent. A associação do épico é ampla. ADR-008 e o Blueprint mantêm a implementação completa do Agente 01 para evolução posterior. P18 permanece **M3 provisório**. A definição de sinais de degradação e gatilhos de retreinamento segue em DOC-02 e carece de decisão G40.

## Recorte de P56 e P57

| Pendência | Dependência já demonstrada | Proposta e condição de validação |
|---|---|---|
| P56 · catálogo, normalização e versionamento | I02 registra fórmulas, versão e linhagem de features de candles. O checkout oficial contém `test_extended_features_known_values` e `test_extended_features_handle_flat_losses_and_empty_volume`. [Features de I02](../evidence/I02-features-adicionais.md) | TS-ST-007/D01 fornece definições e versões das features. TS-ST-013/D02 consome essa versão e deve explicitar a composição e a normalização do vetor. Aprovar catálogo, proprietário por transformação, parâmetros de normalização e regra de compatibilidade. Validar equivalência entre treino e inferência, dados ausentes e corte temporal. |
| P57 · manifestos e reprodução de experimentos | I01 registra origem e checksums das coletas. I02 acrescenta linhagem das janelas. Essas evidências identificam insumos. Não foi localizado um DatasetManifest que congele um dataset de treinamento nem um ensaio de reprodução. [Persistência I01](../evidence/I01-persistencia-btcusdt.md) · [Linhagem I02](../evidence/I02-market-state-multi-intervalo.md) | TS-ST-014 usa o manifesto versionado para rastrear treino e artefato. TS-ST-015/016 em I05 usam o dataset para backtest e walk-forward. Aprovar quem emite e mantém o manifesto, identidade e hashes dos insumos, versões, cortes, partições e ligação ao TrainingRun. Verificar que um dataset identificado pode ser reconstruído e associado a uma repetição controlada do experimento. |

## Decisões e fontes pendentes

| Referência | Decisão ou evidência requerida |
|---|---|
| P07–P09 e P56 | Aprovar schema da observação, ordem e dimensão do vetor, janelas e normalização. Definir fonte e snapshot para Position, Portfolio e Risk State e o comportamento quando qualquer estado estiver ausente ou incompatível. |
| P10/P17 · ADR-009/010 | Aprovar ações e transições por mercado, máscaras e comportamento em pausa ou intervenção. Testar que a intenção produzida passa por Control e Risk. |
| P11/P12 · ADR-012/014 | Aprovar fórmula da reward, coeficientes e limites de fidelidade do ambiente. Os custos e limites sintéticos de I03 servem como cenários de teste. |
| P13/P14/P57 · ADR-013/015/078 | Aprovar contrato de dataset e protocolo de treino reproduzível, com versões, configuração e sementes registradas. Definir o critério de repetição e o limite entre o aceite técnico de I04 e a validação quantitativa de I05. |
| P16 · ADR-016 · F07 | Aprovar schema e ciclo de vida do Registry, autoridade por transição, compatibilidade de observação e rollback. Identificar ata ou decisão existente. A promoção exige decisão humana, e LIVE permanece indisponível. |
| Evidência I04 e G0 | Recuperar eventual candidato I04 com código, suite, manifesto, artefato, resultados e registro de aceite. A inspeção encontrou testes e evidências de dependências, sem comprovação dos critérios de aceite das duas histórias. |

Verificação documental no checkout oficial com PowerShell e `rg`. Os testes de dependência citados foram localizados no código. Os ensaios vinculados são históricos. DOC-03 permanece parcial e G0 segue aberto.
