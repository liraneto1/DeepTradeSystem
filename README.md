# TRADE SYSTEM V1 — Codex Engineering Context Pack

**Baseline de arquitetura:** `TS-ARCH-GLOBAL-V1.0` — aprovada (G01–G60).
**Baseline técnica:** `TS-ENG-I00-V1.0` — aprovada (T01–T10; TS-ADR-089–098).
**Estado de implementação:** ainda não validado. **LIVE:** proibido / não autorizado.

## Como utilizar
1. Copie **todo o conteúdo deste pacote** para a raiz do repositório `DeepTradeSystem`, sem substituir arquivos existentes sem revisar o diff.
2. Abra o repositório no Codex; ele deverá ler `AGENTS.md` antes de alterar arquivos.
3. Leia `docs/00-BASELINE-E-ESCOPO.md`, `docs/01-ARQUITETURA-FISICA.md`, `docs/02-I00-BACKLOG.md`, `docs/03-CONTRATOS.md` e `docs/04-SEGURANCA-E-ACEITE.md`.
4. Faça primeiro **somente** o bootstrap I00-01/I00-02/I00-11. Revise diff, testes e evidências antes de avançar.
5. Os DOCX em `docs/referencias/` são **consolidações reconstruídas**; não substituem o conteúdo original integral das ADRs 001–088 e pendências P01–P106.

## Escopo deste pacote
Este ZIP é **documentação para orientar implementação**, não contém implementação funcional nem credenciais. Schemas em `contracts/examples/` são **exemplos conceituais** sujeitos à validação por JSON Schema na implementação.

## Primeiro comando sugerido ao Codex
Veja `PROMPT-INICIAL-CODEX.md`.

## Bootstrap local

Comece pela [visão inicial da solução](docs/architecture/visao-inicial.md) e
use o [guia de revisão no VS Code](docs/runbooks/revisao-vscode.md) para
acompanhar arquivos, commits e testes.

Com o [uv 0.9.26](https://github.com/astral-sh/uv/releases/tag/0.9.26) disponível no PATH, execute a partir da raiz do repositório:

```sh
uv python install
uv sync --locked
uv run --no-sync ruff check src infrastructure apps tests
uv run --no-sync ruff format --check src infrastructure apps tests
uv run --no-sync mypy
uv run --no-sync pytest
uv build --no-sources
```

Os testes verificam a importação dos 11 pacotes da estrutura modular. A instalação
e as verificações usam o lockfile `uv.lock`. Nenhum serviço local é necessário para
esse conjunto de verificações.

Consulte [as evidências do bootstrap](docs/evidence/I00-bootstrap.md) para acompanhar
o aceite de I00-01, I00-02 e I00-11.

## Banco de desenvolvimento

Veja [PostgreSQL 17 e migrations no VS Code](docs/runbooks/postgresql-local.md) e [Outbox transacional](docs/runbooks/outbox-transacional.md).
