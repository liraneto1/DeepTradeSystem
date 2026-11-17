# Rastreabilidade DOC-03 para I08

**12/11/2026 · IN_REVIEW.** O Blueprint vincula TS-ST-023 a TS-EP-13, que lista P97 e P102–P104 e depende de TS-EP-11 e TS-EP-12. A história exige aprovação formal e versões vinculadas no Evidence Bundle. P100 e P101 são vínculos transversais propostos para critérios quantitativos e evidência de aceite. Esta matriz registra as condições para revisão humana de G4. **LIVE permanece indisponível.**

- [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) · [D06 original](<../referencias/originais/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>) · [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>)
- [Pendências por ID](PENDING-ITEM-RECONCILIATION.md) · [ADRs por ID](ADR-RECONCILIATION.md)

## TS-ST-023 e dependências de G4

| Recorte | Pendências e ADRs | Evidência disponível | Validação necessária |
|---|---|---|---|
| Qualificação PAPER e dependências | P97, P82, P106 · ADR-070/079/082 | As matrizes de I06 e I07 registram as lacunas de G2 e G3. TS-ST-022 tem rastreabilidade em I07 e segue com evidência de homologação pendente. [I06 e G2](DOC-03-I06-TRACEABILITY.md) · [I07 e G3](DOC-03-I07-TRACEABILITY.md) | Vincular o relatório de duração e amostra PAPER e a decisão de G2 aplicável. G4 exige G3 aprovado. Demonstrar que as decisões e evidências dos épicos 11 e 12 se aplicam ao candidato em revisão. |
| Go/No-Go e revalidação | P102 · ADR-062/082/084/087 | A revisão histórica do RC1 registra o aceite do bundle I00 e mantém G0 em aberto. Esse registro ilustra o escopo de uma decisão humana. [Revisão do RC1](../evidence/revisao-g0-i00-rc1.md) | Aprovar autoridade e responsabilidades de decisão, evidências obrigatórias, registro de divergências, validade da decisão e gatilhos de revalidação após mudanças materiais. Registrar parecer humano de gestores autorizados para o candidato identificado. |
| Limites de capital, exposição e monitoramento | P103/P100 e P75/P76 · ADR-064/065/083/085 | I00 tem evidência de correlação diagnóstica. I03 documenta rejeição por limite e custo total com parâmetros sintéticos. [Telemetria](../evidence/I00-10-telemetria.md) · [Custos PAPER](../evidence/I03-custos-paper.md) | Aprovar limites e unidades, escopo por conta e mercado, métricas, alertas e responsáveis. Demonstrar em PAPER os critérios de bloqueio e a rastreabilidade de violações. Os valores sintéticos têm escopo de teste. |
| Suspensão, rollback e retorno a PAPER | P104 e P79/P84 · ADR-026/027/063/081/086 | Os ensaios de I00 e I03 registram reinício, retry, rollback transacional e reconciliação local. [Resiliência I00](../evidence/I00-13-resiliencia.md) · [Livro-razão PAPER](../evidence/I03-persistencia-paper.md) | Aprovar gatilhos, autoridade, critérios de bloqueio e condições de retomada. Exercitar em PAPER suspensão, reconciliação de estado e verificação após recuperação. Rollback de software não reverte efeitos financeiros. |
| Evidence Bundle e versões | P101/P102 · ADR-061/084/087 | O RC1 tem manifesto, resultados e SHA-256, com aceite limitado a I00. [Manifesto RC1](../evidence/releases/i00-rc1/manifest.json) · [Resultados](../evidence/releases/i00-rc1/test-results.json) · [Checksums](../evidence/releases/i00-rc1/SHA256SUMS) | Consolidar a identidade do candidato e versões de código, ambiente, dados, modelo, contratos e políticas aplicáveis. Vincular decisões dos gates, resultados, limites e monitoramento aprovados, ensaios de suspensão, lacunas, riscos e hashes. |

## Condições para revisão de G4

1. Confirmar a decisão humana de G3 e as evidências aplicáveis dos gates anteriores para o candidato. Confirmar o recorte de TS-ST-022 e a evidência de homologação exigida pela baseline.
2. Aprovar a política de capital e exposição, os critérios de monitoramento, o procedimento de suspensão e as condições de revalidação. Validar os cenários permitidos em PAPER.
3. Submeter o Evidence Bundle aos gestores autorizados. Registrar parecer Go/No-Go, escopo, condições, responsável e versões. A matriz mantém a decisão pendente.

A inspeção documental com PowerShell e `rg` localizou o RC1 e evidências de dependência. Não foi localizado dossiê de I08, aprovação de G3 ou decisão humana de G4 no recorte inspecionado. **G4 segue aberto e LIVE permanece indisponível.**
