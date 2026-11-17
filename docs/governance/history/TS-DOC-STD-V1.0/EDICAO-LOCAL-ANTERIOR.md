# TS-DOC-STD-V1.0 — Padrão de documentação

**Estado:** APPROVED · **Data:** 16/11/2026 · **Custódia proposta:** TS-DOC-GOV

## Autoridade e fontes

Aplicar às novas revisões documentais de I00–I09 após aprovação humana. Consultar [AGENTS.md](../../../../AGENTS.md), a [baseline global](<../../../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>), a [baseline técnica](<../../../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>) e os [originais dos domínios](../../../referencias/originais/). Citar caminho e seção ou ID da decisão. Quando a fonte tiver propostas e uma decisão final, citar a decisão final e preservar as propostas como histórico. Um conflito sem resolução explícita entra no Gap Register com as duas fontes. Mudança de baseline segue o processo de decisão aplicável, com ADR e aprovação humana. LIVE permanece indisponível.

## Identidade e versão

Cada documento informa tipo, ID, título, revisão, estado, data, responsável, escopo, fonte e vínculos. Reutilizar IDs existentes (por exemplo, I00, TS-ST-001, I00-AC02, TS-ADR-093 e P18), mantendo a grafia da fonte. Distinguir o ID do objeto da revisão documental e da versão do contrato ou candidato. Para um objeto novo sem ID atribuído, reservar o campo até registro. Usar português no texto e manter identificadores técnicos na forma original. Registrar alterações da revisão e a revisão anterior, quando existir.

## Fluxo e estados

1. Auditar o checkout e suas fontes, registrar artefatos localizados e lacunas, e identificar o recorte da aprovação histórica.
2. Confirmar o catálogo e a prioridade das lacunas com a pessoa responsável. Preencher o template como DRAFT a partir de fontes verificadas.
3. Enviar a revisão identificada para análise, com rastreabilidade e questões explícitas. Registrar IN_REVIEW.
4. Registrar APPROVED somente com decisão humana identificável, data, revisão ou candidato, escopo e condições. Se houver alteração material, abrir nova revisão para análise e conservar a decisão anterior no registro. Usar SUPERSEDED com referência ao substituto aprovado.
5. Engenharia usa a revisão aprovada para executar e devolver testes e evidências. Registrar execução, conclusão técnica e decisão de gate em campos distintos.

MISSING sinaliza artefato esperado e ausente no recorte auditado. Usar “Fonte pendente” com referência ao Gap Register para campos desconhecidos e “Não aplicável” com justificativa para exclusões. Um link registrado indica rastreabilidade. Resultado de teste requer execução identificável e aceite requer a decisão correspondente.

## Rastreabilidade e evidência

Vincular fonte, decisão/ADR, pendência, incremento, épico, feature, história/pacote, critério, contrato, teste, evidência e decisão, conforme aplicável. Preservar mapeamentos múltiplos e justificar vínculos parciais ou ainda desconhecidos. Registrar por evidência o ambiente, commit e estado do checkout ou digest, versões, comando/execução, esperado, observado, limitações, arquivos e integridade. Sanitizar logs e exemplos. Preservar o resultado original e anexar novas execuções com a própria identidade.

## Registros e templates

- [Document Registry](../../DOCUMENT-REGISTRY.md)
- [Gap Register](../../GAP-REGISTER.md)
- [Traceability Matrix](../../REQUIREMENTS-TRACEABILITY-MATRIX.md)
- [Approval Register](../../APPROVAL-REGISTER.md)

Os sete templates a seguir foram aprovados em 16/11/2026 com o padrão. O campo `Estado: DRAFT` é o estado inicial de cada documento criado a partir deles. [Decisão de aprovação](../../APPROVAL-REGISTER.md)

Templates em Markdown para [Incremento](../../templates/INCREMENTO.md), [Épico](../../templates/EPICO.md), [Feature](../../templates/FEATURE.md), [História Técnica](../../templates/HISTORIA-TECNICA.md), [Contrato](../../templates/CONTRATO.md), [Teste](../../templates/TESTE.md) e [Evidência](../../templates/EVIDENCIA.md).
