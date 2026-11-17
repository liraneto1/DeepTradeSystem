# AC02 Compatibilidade Linux e auditoria complementar

**12/11/2026 · candidato d561026f27fa3920699af41aeea6e1a60bcf89a6.** LIVE permanece indisponível.

## Linux e PostgreSQL

O [run 43308853482](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43308853482/job/131499228992) já executou o SHA exato em 12/11/2026. O job quality terminou com sucesso em Ubuntu x64, Python 3.12.12. O log confirma checkout do SHA, instalação com lockfile, lint, formatação, mypy e build de wheel e sdist. A suíte geral teve 105 aprovados e 38 pulados. A etapa PostgreSQL teve **38 aprovados**, com PAPER, LIVE_ENABLED=false e RUN_POSTGRES_TESTS=1. A revisão recuperou a execução existente.

## Imagem PostgreSQL

O CI usou a tag postgres:17. O log informa prefixos de camadas e não informa o digest do manifesto. A resolução da tag em 12/11 retornou índice sha256:846a7ddaa67a4b354ae1d21087b683901aa6113a4ed626d3787cfbf6c85e3e07 e manifesto linux/amd64 sha256:6f7593c161689b6b02c78668b314af7da8811b592c5519108c57a49d0b6ad788. As camadas divergem das do CI. Por exemplo, o prefixo 56c5b61c6d2b aparece no CI e está ausente do manifesto consultado.

Trivy 0.76.2, com ZIP verificado pelos checksums publicados, executou scan remoto de vulnerabilidades no digest 6f7593c. Base v2 atualizada em 2026-11-12T18:57:38Z. Resultado: Debian 13.7, 548 ocorrências Debian e 62 no binário gosu. Por gravidade: 2 críticas, 149 altas, 176 médias, 154 baixas e 129 desconhecidas. As duas críticas reportadas são CVE-2026-6653 em libxml2 e CVE-2025-68121 na stdlib Go de gosu. Os achados do scanner aguardam triagem de aplicabilidade. [Relatório bruto Trivy](AC02-postgres-6f7593c-trivy.json)

SHA-256 do relatório: 83e160d10c21c517d675b51b3dfaac6949e174aa5f0d6df4b12032860ec498b6

## Build e componentes nativos

O cache do build Windows contém Hatchling 1.28.0, packaging 26.3, pathspec 1.1.1, pluggy 1.7.0 e trove-classifiers 2026.9.21.13. Consulta OSV por nome e versão de 12/11 retornou zero correspondências para esses cinco pares PyPI. Falta confirmar o conjunto isolado do build Linux.

O wheel Windows de psycopg-binary 3.3.8 contém libpq 18.4 e OpenSSL 3.6.5. O Python Windows reportou OpenSSL 3.5.4. A consulta NVD por CPE retornou 62 correspondências para OpenSSL 3.5.4 e 30 para PostgreSQL 18.4. São resultados brutos. O CPE de PostgreSQL cobre o produto e requer triagem para determinar aplicabilidade ao cliente libpq. A consulta de OpenSSL 3.6.5 expirou. Falta inventariar e auditar as bibliotecas incorporadas ao wheel Linux e os demais binários no escopo. [Inventário Windows](AC02-d561026.json)

## Parecer pendente

Compatibilidade Linux e integração PostgreSQL demonstradas no SHA candidato. Para concluir AC02, recuperar o manifesto exato do CI ou repetir a integração com um digest explícito e auditado. Triar os achados de imagem e componentes nativos, registrar correções ou exceções e obter parecer humano de Engenharia, QA e Segurança. AC02 continua em validação. G0 segue aberto.
