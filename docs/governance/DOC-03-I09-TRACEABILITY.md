# Rastreabilidade DOC-03 para I09

**12/11/2026 · IN_REVIEW.** O Blueprint vincula TS-ST-024 (avaliação pós-LIVE) a TS-EP-14, dependente de TS-EP-13 e das evidências de I08. A história exige métricas, limites e revalidação documentados. O épico remete a pendências M2/M3 conforme decisão, sem atribuir IDs individuais. Os vínculos abaixo são propostas de refinamento e não alteram as fases. **LIVE permanece indisponível.**

- [Blueprint original, roadmap, TS-EP-14, linha 2042 e tabela de gates](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)
- [D07 original, tabela de gates](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) · [Pendências por ID](PENDING-ITEM-RECONCILIATION.md) · [ADRs por ID](ADR-RECONCILIATION.md)

| Recorte de TS-ST-024 | Pendências e ADRs | Evidência disponível e validação pendente |
|---|---|---|
| Histórico e limites do candidato I08 | P103/P106 · ADR-082/085 | A matriz de I08 registra G4 em aberto e as dependências de G3 e TS-ST-022. Para G5, a baseline exige histórico de I08 e evidência de respeito aos limites aprovados, vinculados às versões e decisões aplicáveis. Esse histórico não foi localizado. [I08 e G4](DOC-03-I08-TRACEABILITY.md) |
| Métricas de estabilidade, qualidade e risco | P100/P105, com dependência de P75/P76 · ADR-064/065/083 | I00 tem correlação diagnóstica e I03 registra reconciliação e recuperação local. Aprovar métricas, fontes, janela, cobertura, limites e critérios de qualidade dos registros. A revisão de G5 requer histórico suficiente para avaliar estabilidade, incidentes, divergências e risco residual. [Telemetria I00](../evidence/I00-10-telemetria.md) · [Recuperação PAPER](../evidence/I03-recuperacao-marcacao-paper.md) |
| Reavaliação de risco, mudanças e suspensão | P102/P103/P104 · ADR-084/085/086 | I08 documenta decisões ainda pendentes. Os ensaios de I00 e I03 são referências para recuperação e reconciliação. Aprovar condições de revalidação após mudanças materiais, critérios de suspensão, responsáveis e encaminhamento das exceções antes de qualquer nova decisão. [Resiliência I00](../evidence/I00-13-resiliencia.md) · [Reconciliação PAPER](../evidence/I03-persistencia-paper.md) |
| Evidence Bundle e decisão humana | P101/P102 · ADR-082/087 | O RC1 é referência para manifesto, integridade e registro de aceite de escopo restrito. Para G5, reunir candidato, versões, resultados, incidentes, reconciliações, avaliação atualizada de risco e hashes. Vincular o parecer de Gestores e Risk ou dos responsáveis designados, com decisão, escopo e condições. [Manifesto RC1](../evidence/releases/i00-rc1/manifest.json) · [Revisão RC1](../evidence/revisao-g0-i00-rc1.md) |

## Validação de G5

O Blueprint exige histórico de LIVE limitado em I08, estabilidade e nova avaliação de risco. D07 exige estabilidade dentro dos limites. A duração, a amostra, os limiares e a autoridade nominal de decisão ainda precisam de validação. A revisão deve conferir a decisão prévia de G4, o histórico e suas versões, os resultados frente aos limites e o novo parecer humano. Qualquer seleção de pendências M2/M3 para TS-EP-14 deve ter decisão rastreável. P18 segue M3 provisório e sem atribuição a I09.

A inspeção documental com PowerShell e `rg` não localizou histórico autorizado de I08, Evidence Bundle de I09 ou decisão humana de G5 no recorte inspecionado. Os ensaios PAPER fornecem evidência de dependência. **G5 segue aberto e LIVE permanece indisponível.**
