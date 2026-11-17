# AC02 Critérios de aceite para engenharia

**12/11/2026 · APPROVED · critérios aprovados pelo usuário nesta conversa em 12/11/2026 · candidato `d561026f27fa3920699af41aeea6e1a60bcf89a6`.** Este roteiro detalha as validações restantes de I00-AC02 e DOC-06. LIVE permanece indisponível. Qualquer reexecução de integração usa PAPER, `LIVE_ENABLED=false`, credenciais de teste e banco descartável isolado.

## Evidência de partida

O job Linux amd64 de 12/11 confirmou o SHA e o lockfile do candidato, PostgreSQL 17.12 e o digest `sha256:6f7593c161689b6b02c78668b314af7da8811b592c5519108c57a49d0b6ad788`. Os **38 testes PostgreSQL passaram**. O relatório Trivy desse digest registra 2 ocorrências críticas e 149 altas. O wheel manylinux de `psycopg-binary` foi conferido contra o lockfile e a inspeção estática identificou 15 bibliotecas incorporadas. O build Linux passou e o conjunto efetivamente resolvido no seu ambiente isolado ainda precisa ser comprovado.

[Job de integração](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43324339962/job/131552874577) · [Triagem inicial](../evidence/AC02-d561026-digest-triage.md) · [Inventário Windows e hash do lockfile](../evidence/AC02-d561026.json)

## Validações e critérios de aceite

| Frente | Entrega esperada dos agentes de engenharia | Critério de aceite aprovado |
|---|---|---|
| Imagem PostgreSQL | Vincular manifesto e plataforma do container ao job e ao relatório de varredura. Registrar versão da ferramenta, data da base, inventário de pacotes e binários e triagem dos achados por componente e versão. Documentar aplicabilidade, alcance no ambiente de teste, correção ou risco residual. | Digest testado e digest auditado coincidem. Cada achado tem disposição rastreável, individualmente ou por grupo com justificativa comum. A triagem trata explicitamente libxml2 e a biblioteca padrão Go incorporada em gosu. Qualquer risco residual aceito tem justificativa, responsável, validade e decisão de Segurança. Se houver troca de digest, auditar a nova imagem e repetir a integração vinculando o resultado a ela. |
| Componentes nativos Linux | Inventariar os wheels e binários selecionados no runner e os componentes nativos no escopo da release, incluindo CPython e as bibliotecas incorporadas a `psycopg-binary`. Registrar origem, versão efetiva, backports ou atestação quando disponíveis, hashes e vínculo ao artefato instalado ou carregado. Consultar avisos aplicáveis e registrar os limites da fonte. | O inventário identifica os artefatos efetivos e permite reproduzir a associação com os avisos. Nomes de arquivos e SONAMEs servem como pista. Versões desconhecidas ou ausência de fonte permanecem como lacunas com tratamento explícito. A triagem distingue bibliotecas cliente de vulnerabilidades exclusivas do servidor e registra correção ou decisão sobre o risco residual. |
| Build isolado Linux | Capturar Python, uv, backend e versões diretas e transitivas resolvidas no ambiente isolado do build. Incluir Hatchling 1.28.0 e suas dependências efetivas, com origem, versão e hash ou identificação equivalente. Consultar avisos para esse conjunto e anexar logs e hashes de wheel e sdist. | Um build limpo vinculado ao candidato produz os artefatos e um inventário Linux verificável, com resultado de auditoria e tratamento dos achados. O lockfile do projeto e o inventário de build Windows são referências complementares. Se o conjunto de build mudar materialmente, repetir as verificações afetadas. |

[Relatório Trivy por digest](../evidence/AC02-postgres-6f7593c-trivy.json) · [Evidência Linux e segurança](../evidence/AC02-d561026-linux-security.md)

## Registro para decisão humana

O Evidence Bundle deve ligar commit, SHA-256 do lockfile, plataforma, digest, identidade dos artefatos, execução de CI, inventários e relatórios de auditoria. Para cada achado ou lacuna, registrar fonte, aplicabilidade, resolução ou exceção, evidência, responsável e prazo quando aplicável. Engenharia e QA revisam compatibilidade e rastreabilidade. Segurança revisa a triagem e os riscos residuais. Os responsáveis nominais precisam ser confirmados na revisão.

AC02 pode ser submetido a aceite quando as três frentes tiverem evidência vinculada ao candidato e as lacunas ou exceções tiverem tratamento formal. A aprovação humana abrange os critérios desta ficha. A decisão de aceite de AC02 depende das evidências e do parecer. [Repasse a Engenharia](AC02-ENGINEERING-HANDOFF.md) **AC02 continua em validação e G0 permanece aberto.** [DOC-06](DOC-06-RELEASE-DEPENDENCIES.md) · [Dossiê de G0](G0-REVIEW-DOSSIER.md)
