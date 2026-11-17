# Repasse de AC02 aos agentes de engenharia

**12/11/2026 · Pronto para repasse.** O usuário aprovou nesta conversa os [critérios de aceite de AC02](AC02-ENGINEERING-ACCEPTANCE.md) para o candidato `d561026f27fa3920699af41aeea6e1a60bcf89a6`. AC02 aguarda execução das validações restantes e parecer humano. G0 segue aberto. **LIVE permanece indisponível.**

## Ponto de partida

- O job Linux amd64 executou **38 testes PostgreSQL com sucesso** no SHA indicado, com PostgreSQL 17.12 e imagem `docker.io/library/postgres@sha256:6f7593c161689b6b02c78668b314af7da8811b592c5519108c57a49d0b6ad788`. O SHA-256 do lockfile é `e40093ac899ba45d0d9290942cb66553fc02722d55f7cceeba70f26713970919`. [Job de integração](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43324339962/job/131552874577)
- Os registros existentes incluem a triagem inicial da imagem, a conferência do wheel Linux de psycopg-binary e os resultados de build. [Triagem inicial](../evidence/AC02-d561026-digest-triage.md) · [DOC-06](DOC-06-RELEASE-DEPENDENCIES.md)

## Instruções para Engenharia

Trabalhe no checkout oficial de DeepTradeSystem e siga AGENTS.md. Qualquer reexecução de integração usa Linux amd64, banco descartável isolado, credenciais de teste, PAPER e `LIVE_ENABLED=false`.

1. **Imagem PostgreSQL.** Confirme manifesto, plataforma e identidade do container contra o job e o relatório Trivy. Triar os achados, incluindo libxml2 e Go em gosu, por componente e versão. Registre aplicabilidade, alcance, correção ou risco residual. Se o digest mudar, audite o novo digest e repita a integração em PAPER. [Relatório Trivy](../evidence/AC02-postgres-6f7593c-trivy.json)
2. **Componentes nativos Linux.** Identifique os artefatos instalados ou carregados no runner, incluindo CPython e bibliotecas incorporadas a psycopg-binary. Registre origem, versão, hashes, backports ou atestação quando disponíveis. Consulte os avisos aplicáveis e preserve como lacunas as versões ou origens sem comprovação. Distinga componentes cliente de avisos exclusivos do servidor.
3. **Build isolado Linux.** Capture Python, uv, Hatchling e as dependências efetivamente resolvidas no ambiente de build, com origem, versão e identificação do artefato. Audite esse conjunto. Anexe logs do build e os hashes do wheel e do sdist.

## Retorno a TS-DOC-GOV

Entregue as referências ao commit, lockfile, digest, plataforma e execução, mais os inventários, relatórios e hashes. Para cada achado ou lacuna, indique fonte, evidência, aplicabilidade, resolução ou exceção proposta, responsável e prazo quando aplicável. Identifique o que foi executado e o que ficou pendente. Engenharia e QA revisam compatibilidade e rastreabilidade. Segurança avalia os achados e o risco residual. TS-DOC-GOV incorpora as evidências e registra o parecer humano quando emitido. [Dossiê de G0](G0-REVIEW-DOSSIER.md)
