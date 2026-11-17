# Rastreabilidade DOC-03 para I05

Registro de 12/11/2026 em `IN_REVIEW`. O Blueprint liga I05 a TS-EP-08 e às histórias TS-ST-015 e TS-ST-016. O épico lista P91–P95 e P100 e depende de TS-EP-03, TS-EP-06 e TS-EP-07. A associação de P57 e das demais pendências transversais às histórias abaixo é proposta de refinamento. Referências do Blueprint: roadmap, TS-EP-08, linhas 2033–2034 e critérios de aceite por incremento.

- [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) · [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>)
- [Pendências](PENDING-ITEM-RECONCILIATION.md) · [ADRs](ADR-RECONCILIATION.md) · [I01/I02](DOC-03-I01-I02-TRACEABILITY.md) · [I03](DOC-03-I03-TRACEABILITY.md) · [I04](DOC-03-I04-TRACEABILITY.md)

## Histórias e evidências

| História e recorte | Componente e artefato | Pendências e ADRs | Evidência disponível e lacuna |
|---|---|---|---|
| TS-ST-015 · backtest realista · custos, funding e execução simulada | D07-C03 com D03-C02/C03 · execução histórica simulada, fills e trilha de PnL | P21/P24/P91 · ADR-022/053/074/075 | O checkout oficial contém `test_paper_costed_fills_replay_and_reconcile` e `test_futures_funding_cutoff_replay_and_reconciliation`. Os ensaios de I03 cobrem custos e funding em PAPER. Falta execução histórica de I05 com hipóteses de latência, política de fills e reconciliação do PnL líquido. [Testes de integração](../../tests/integration/test_postgres_migrations.py) · [Custos](../evidence/I03-custos-paper.md) · [Funding](../evidence/I03-funding-paper.md) |
| TS-ST-015 · margem, alavancagem e liquidação | D07-C03 com D03-C01/C03 · estado de margem, posição e preço de marcação | P20/P25/P92 · ADR-019/020/023/074/075 | `test_futures_liquidation_margin_cutoff_and_reconciliation` e o ensaio de liquidação são referências para invariantes. Falta validar o mesmo comportamento em replay histórico com dados e parâmetros versionados. [Liquidação PAPER](../evidence/I03-liquidacao-paper.md) |
| TS-ST-016 · walk-forward e avaliação fora da amostra (OOS) | D07-C03, D02-C03 e D05-C04 · protocolo cronológico, janelas e resultados OOS | P13/P55/P56/P57/P93/P95 · ADR-015/047/048/076/078 | `test_multi_interval_uses_only_aligned_and_available_candles` cobre disponibilidade em Market State. A linhagem e os checksums de I01/I02 sustentam a origem dos insumos. Falta uma execução por janela com treino, validação, OOS, embargo quando aplicável e prova de ausência de vazamento temporal. [Teste de Market State](../../tests/unit/test_market_state.py) · [Linhagem I02](../evidence/I02-market-state-multi-intervalo.md) |
| TS-ST-016 · benchmarks e robustez | D07-C03 e D02-C03 · relatório comparativo por janela e regime | P14/P94/P95/P100 · ADR-013/076–078/083 | D02/D07 registram a comparação com benchmarks e avaliação de robustez. Falta relatório que compare modelos e referências sob o mesmo recorte de dados, custos e execução simulada. A matriz de I04 também não identificou um candidato PPO rastreável. [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) · [Matriz I04](DOC-03-I04-TRACEABILITY.md) |
| TS-ST-015/016 · reprodução e aceite quantitativo | D05-C04 e D07-C03/C06 · DatasetManifest, BacktestRunManifest e evidência para G1 | P57/P95/P100 · ADR-048/078/082/083/087 | D07 define BacktestRunManifest como identidade e configuração do backtest. No recorte inspecionado não foram localizados manifesto I05, execução de backtest, relatório OOS ou decisão humana de G1. [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) |

Os testes acima foram localizados no checkout oficial. Os resultados vinculados são evidências de dependência de I01–I03, com o escopo indicado em cada registro.

## P57 e P95 na cadeia de reprodução

1. **P57 · DatasetManifest.** Os manifestos de coleta de I01 identificam arquivos e hashes. I02 acrescenta linhagem e versão de features. O manifesto de dataset precisa fixar quais insumos, versões de features e observação, cortes de disponibilidade e partições compõem o dataset usado. O vínculo proposto é TS-ST-014 como consumidor no treino e TS-ST-015/016 como consumidores na avaliação. [Persistência I01](../evidence/I01-persistencia-btcusdt.md) · [Features I02](../evidence/I02-features-adicionais.md)
2. **P95 · BacktestRunManifest.** O manifesto da execução deve referenciar a identidade do dataset, versão do código, modelo ou benchmark, parâmetros de simulação, janelas, sementes quando aplicáveis e artefatos de saída. A seleção ou ajuste de parâmetros por janela deve ser rastreável. A aprovação desses campos e do critério de reprodução ainda está pendente. [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>)

A evidência esperada é reconstituir o dataset identificado e repetir uma execução de referência, conferindo os artefatos e as métricas por janela conforme a tolerância aprovada. Para OOS, o teste deve demonstrar que seleção, ajuste e normalização não usam informações do período avaliado. O dono e os schemas dos dois manifestos permanecem em validação.

## Decisões e fontes pendentes

| Referência | Decisão ou evidência necessária |
|---|---|
| P91/P92 · TS-ST-015 | Aprovar fontes e versões para taxas, funding, latência, slippage e preço de marcação, além das regras de preenchimento, margem e liquidação em replay. Os parâmetros sintéticos de I03 são casos de teste. |
| P13/P93 · TS-ST-016 | Aprovar janelas, regra de reestimação, política de embargo conforme sobreposição e critério de independência OOS. Vincular os resultados a cada partição. |
| P94 · TS-ST-016 | Aprovar a lista de benchmarks, incluindo quais comparações de D02 entram no recorte, a regra de comparação sob condições equivalentes e os testes de sensibilidade e regimes. |
| P57/P95 · ambas as histórias | Definir responsáveis, schema e local de publicação dos manifestos. Recuperar candidato de I04, fontes de dados e artefatos necessários ao primeiro ensaio de reprodução. |
| P14/P100 · G1 | Aprovar métricas, limites de aceite, cobertura mínima e processo de decisão humana. Recuperar eventual relatório existente com commit, dataset, configuração e resultados por janela. |

Verificação documental no checkout oficial com PowerShell e `rg`. Os testes citados foram inspecionados pelo nome e as evidências foram vinculadas às fontes locais. DOC-03 permanece parcial. G0 e G1 seguem abertos.
