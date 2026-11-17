# Auditoria documental — I00

**Estado:** DRAFT · **Data:** 16/11/2026 · **Checkout:** HEAD `184e8b30a8dc9d812bce092e893f70a8931c4570`, com alterações locais preexistentes.

## Recorte

Foram inventariados 158 arquivos antes desta revisão, incluindo 117 Markdown, em `docs/`, `contracts/` e os três guias da raiz. Marcadores de diretório e atributos Git foram excluídos. A revisão cruzou as instruções de trabalho, baselines, ADRs, matrizes, registros de decisões, contratos e retornos de Engenharia. A verificação dos destinos de links relativos Markdown em sintaxe inline não apontou arquivos ausentes. O teste verificou a existência do destino no checkout, sem validar âncoras, links externos ou o conteúdo de arquivos fora do recorte.

## Achados

| Grupo | Achado e tratamento |
|---|---|
| Fontes e ADRs | Os TXT em originais têm autoridade declarada. A reconciliação indexa ADR-001–098, e as fichas ADR-017–028 de D03 estão no checkout. A aprovação dos resumos técnicos continua válida no escopo original. Campos sem fonte para fichas individuais seguem explicitados. [Fontes](SOURCE-RECOVERY.md) · [ADRs](ADR-RECONCILIATION.md) |
| Inventário e lacunas | O catálogo histórico já existe e recebe complemento dos arquivos localizados. A análise anterior preserva a cronologia. O Gap Register aponta o estado atual e a decisão ou evidência requerida. [Catálogo](DOCUMENT-REGISTRY.md) · [Lacunas](GAP-REGISTER.md) |
| Vínculos e evidências | O mapa de I00 registra 14 pacotes e 12 critérios, com quatro histórias iniciais detalhadas no DOC-03. Os resultados de RC1, AC02, AC07 e AC09 pertencem a recortes distintos. [Matriz](REQUIREMENTS-TRACEABILITY-MATRIX.md) · [DOC-03 I00](DOC-03-I00-TRACEABILITY.md) |
| Decisões | As aprovações de baseline, recortes, bundle e políticas têm escopos próprios. A aprovação do padrão e a decisão de G0 continuam pendentes. [Aprovações](APPROVAL-REGISTER.md) |

A auditoria documental não repetiu testes de produto ou de segurança. LIVE permanece indisponível.
