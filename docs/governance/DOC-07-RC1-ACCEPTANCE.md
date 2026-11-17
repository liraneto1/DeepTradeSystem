# DOC-07 Aceite do Evidence Bundle I00 RC1

**Consolidação de 12/11/2026.** O usuário aprovou I00-14 e o Evidence Bundle `i00-rc1` em **11/11/2026**, conforme o registro de revisão. O aceite cobre o bundle de I00 e evidencia **I00-AC12** para o candidato `8d1467dd4087bcb6bb37fd4cc880de6d42b661e6`, cuja publicação consta no registro como `3488ddd`. A decisão humana de **G0 segue aberta**. LIVE permanece indisponível.

[Registro do aceite de 11/11](../evidence/revisao-g0-i00-rc1.md) · [Registro mestre I00](../backlog/registro-mestre-i00.md) · [Critérios de aceite](../04-SEGURANCA-E-ACEITE.md)

## Evidências de AC12

| Evidência | O que comprova no escopo de I00-14 |
|---|---|
| [Manifesto](../evidence/releases/i00-rc1/manifest.json) e [guia do bundle](../evidence/releases/i00-rc1/README.md) | Identidade do candidato, baselines, versões de contratos, migrations, configuração sanitizada e identificação dos artefatos. |
| [Resultados do RC1](../evidence/releases/i00-rc1/test-results.json) | Resultados históricos vinculados ao commit candidato. O CI registra 69 testes gerais aprovados e 16 integrações aprovadas em PostgreSQL 17. |
| [Amostra de diagnóstico](../evidence/releases/i00-rc1/diagnostic-log.json) | Registro sanitizado de diagnóstico para o recorte documentado. |
| [SHA256SUMS](../evidence/releases/i00-rc1/SHA256SUMS) | Oito hashes conferidos novamente no checkout oficial em 12/11 com PowerShell e `Get-FileHash -Algorithm SHA256`. São cinco arquivos de evidência e três artefatos locais, incluindo ZIP, sdist e wheel. |
| [Revisão de 11/11](../evidence/revisao-g0-i00-rc1.md) | Aceite humano de I00-14 e do bundle RC1. O campo `bundle_acceptance` do manifesto conserva o estado histórico anterior à revisão. O aceite posterior está neste registro de revisão. |

A conferência foi de integridade e rastreabilidade. Os resultados de testes e build são históricos.

## Pendências para a decisão de G0

1. **Consolidar o candidato de engenharia.** Vincular código, CI, contratos, testes e evidências de conformidade de I01–I04 ao candidato ou às versões que a revisão abranger. Incluir dados de mercado, features e Market State, Trading Core PAPER e observação, treino e registro de modelos. [Consolidação DOC-03](DOC-03-CONSOLIDATION.md)
2. **Tratar as ressalvas de I00.** Validar conflitos e lacunas permanentes para AC07, demonstrar métricas da Outbox para AC09 e completar a avaliação de compatibilidade e segurança para AC02. Registrar o tratamento formal de qualquer lacuna aceita, com responsável e justificativa. [DOC-04](DOC-04-OUTBOX-ORDERING.md) · [DOC-05](DOC-05-OUTBOX-METRICS.md) · [DOC-06](DOC-06-RELEASE-DEPENDENCIES.md)
3. **Registrar decisão humana de G0.** Confirmar responsáveis de Engenharia e QA, critérios aplicáveis, escopo e versões revisadas. Registrar data, parecer, evidências, ressalvas e encaminhamento. G49 mantém o aceite por incremento e as decisões de gate independentes. [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>)

**Estado de DOC-07.** Aceite de I00-14 e do Evidence Bundle RC1 consolidado. AC12 evidenciado no escopo do RC1. Decisão de G0 pendente.

[Dossiê de revisão de G0](G0-REVIEW-DOSSIER.md).
