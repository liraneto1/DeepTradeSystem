# DOC-06 Compatibilidade e segurança das dependências da release

**12/11/2026 · DRAFT.** Avaliação documental de I00-AC02, vinculada a I00-02, I00-11, TS-ADR-094/095 e P80. O recorte comprovado é o candidato I00 RC1, commit `8d1467dd4087bcb6bb37fd4cc880de6d42b661e6`. AC02 tem evidência de dependências controladas e compatibilidade no recorte ensaiado. A avaliação de segurança e o aceite do conjunto de dependências permanecem abertos. G0 segue aberto. LIVE permanece indisponível.

[Manifesto RC1](../evidence/releases/i00-rc1/manifest.json) · [Resultados RC1](../evidence/releases/i00-rc1/test-results.json) · [Revisão RC1](../evidence/revisao-g0-i00-rc1.md)

## Avaliação e evidências disponíveis

| Aspecto | Evidência e conclusão |
|---|---|
| Identidade do conjunto | O ZIP do RC1 contém um `uv.lock` com 59 entradas de pacote, incluindo o projeto e grupos de dependências. SHA-256 dos bytes do lockfile no ZIP: `cdfd21d135ffbf1ffcb93104bfce3721fc35d00c218e31e2b6090d436bf70d71`. Oito de oito hashes do bundle conferiram no checkout oficial. [Checksums](../evidence/releases/i00-rc1/SHA256SUMS) |
| Compatibilidade exercitada | Os resultados históricos registram `uv sync --locked`, lint, formatação, mypy e build bem-sucedidos em Windows x64 e no CI Ubuntu. O registro local indica Python 3.12.12 e uv 0.9.26. A suíte geral registra 69 aprovados e 16 pulados. O CI registra 16 testes PostgreSQL 17 aprovados na etapa de integração. A cobertura se restringe a esses ambientes e cenários. [Resultados](../evidence/releases/i00-rc1/test-results.json) |
| Integridade e build | O RC1 registra dois builds equivalentes no mesmo ambiente. As GitHub Actions do snapshot são fixadas por SHA. A imagem PostgreSQL usa a tag `postgres:17`. Falta registrar o digest efetivo da imagem e a identidade dos demais insumos de build para verificar reprodução em outro ambiente. |
| Segurança das dependências | O lockfile e os hashes controlam resolução e integridade do bundle. A inspeção dos documentos e do workflow não encontrou SBOM ou relatório de auditoria de vulnerabilidades associado ao candidato. Sem esse resultado, exposição, aplicabilidade e risco residual permanecem sem avaliação conclusiva. |
| Checkout oficial | Após normalizar finais de linha, `.python-version` e o Compose coincidem com o snapshot. `uv.lock`, `pyproject.toml` e o workflow diferem. O aceite e os resultados do RC1 se aplicam ao seu snapshot. [Lockfile atual](../../uv.lock) · [Workflow atual](../../.github/workflows/ci.yml) |

## Validação pendente para AC02

1. **Fixar o recorte.** Registrar commit, hash do lockfile, grupos instalados, sistema e arquitetura, Python, uv, backend e dependências de build, Actions, imagem e digest. Inventariar dependências diretas e transitivas resolvidas, inclusive binários distribuídos com pacotes e componentes da imagem no escopo. Registrar responsáveis e plataformas que a release precisa suportar.
2. **Demonstrar compatibilidade.** Para cada plataforma aprovada, executar instalação limpa com `uv sync --locked`, build e verificações de import, contratos e integração PostgreSQL aplicáveis. Registrar versões efetivamente resolvidas, falhas, skips e resultados por candidato. Repetir a análise após mudança material do conjunto.
3. **Demonstrar segurança.** Gerar inventário ou SBOM do candidato e auditar as versões resolvidas e a imagem aplicável. Registrar ferramenta, versão, fonte e data da base de avisos, cobertura, achados e avaliação de aplicabilidade. Definir correções ou exceções justificadas com responsável, prazo e decisão humana. Validar origem dos artefatos e critérios de aceite de risco residual.
4. **Consolidar o parecer.** Anexar inventário, relatórios de compatibilidade e segurança, hashes e decisão ao Evidence Bundle. Engenharia e QA revisam os resultados. Segurança avalia achados e exceções conforme responsabilidades a confirmar.

Nesta revisão foram usados PowerShell, leitura do ZIP, `Get-FileHash` e `rg`. A verificação foi documental. Não foram executados novo build, suíte de compatibilidade ou scanner. **DOC-06 segue aberto e AC02 mantém a ressalva de segurança e compatibilidade da release.**


## Validação de AC02 no candidato d561026

Em 12/11/2026 foi verificado o commit `d561026f27fa3920699af41aeea6e1a60bcf89a6`. O checkout tinha alterações documentais e a comparação com HEAD não mostrou diferenças rastreadas nas áreas de código, testes, dependências, CI e deploy inspecionadas. O inventário registra o SHA-256 local do lockfile e os hashes dos artefatos gerados.

- Windows x64, Python 3.12.12 e uv 0.9.26. A venv existente falhou na coleta por dependências ausentes. Em venv temporária, `uv sync --locked` passou. `pytest` registrou 105 aprovados e 38 pulados, com PostgreSQL desativado na execução. `uv build --no-sources` gerou wheel e sdist.
- A consulta OSV retornou 58 respostas para 58 dependências PyPI instaladas, com zero correspondências para os pares nome/versão consultados. O inventário inclui o grupo de desenvolvimento e confere com as versões do lockfile. A cobertura se limita aos pacotes Python instalados no Windows e aos avisos indexados no instante da consulta.
- Faltam Linux/CI e integração PostgreSQL no mesmo candidato, digest e auditoria da imagem PostgreSQL e avaliação dos componentes nativos e de build fora do inventário Python. Confirmar plataformas suportadas e registrar parecer humano de Engenharia, QA e Segurança.

AC02 permanece em validação. G0 segue aberto. LIVE permanece indisponível.

[Inventário, resultados e hashes de build](../evidence/AC02-d561026.json)

## Complemento de AC02 para d561026

O CI Linux do SHA exato passou, incluindo 38 testes PostgreSQL em PAPER. A imagem atual foi auditada por digest e difere da imagem observada no CI. A identificação do digest histórico, a triagem dos achados e a cobertura nativa e de build restante seguem pendentes. [Evidência Linux e segurança](../evidence/AC02-d561026-linux-security.md)

## Triagem complementar e repetição por digest

O wheel Linux de psycopg-binary foi conferido contra o lockfile. A triagem da imagem identificou libxml2 afetado e documentou a hipótese de baixa aplicabilidade do achado TLS de gosu. A repetição por digest requer runner Linux com Docker. A triagem completa e o inventário do build Linux permanecem pendentes. [Evidência e instruções de repetição](../evidence/AC02-d561026-digest-triage.md)

[Critérios de aceite de AC02 para os agentes de engenharia](AC02-ENGINEERING-ACCEPTANCE.md).

O retorno parcial de Engenharia de 13/11/2026 foi incorporado ao [dossiê de G0](G0-REVIEW-DOSSIER.md). A triagem de aplicabilidade, os inventários efetivos e o parecer humano seguem pendentes.

O retorno parcial de Engenharia de 13/11/2026 foi incorporado ao [dossiê de G0](G0-REVIEW-DOSSIER.md). A triagem de aplicabilidade, os inventários efetivos e o parecer humano seguem pendentes.
