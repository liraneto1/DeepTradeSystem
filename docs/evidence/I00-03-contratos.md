# Evidências de I00-03

Validação em 11/11/2026 no checkout do OneDrive, com Windows x64, Python 3.12.12
e uv 0.9.26. A entrega segue TS-ADR-097 e TS-ADR-098 e fornece evidência local
para I00-AC03. Veja os [schemas, exemplos e limites da validação](../03-CONTRATOS.md).

| Verificação | Resultado observado |
|---|---|
| `uv sync --locked` | 35 pacotes conferidos, com jsonschema 4.26.0. |
| `uv run --no-sync ruff check src tests` | Sem violações. |
| `uv run --no-sync ruff format --check src tests` | 14 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 14 arquivos-fonte. |
| `uv run --no-sync pytest` | 39 testes passaram, incluindo 28 de contrato. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

A instalação inicial falhou com o erro 396 do Windows ao criar hardlinks.
Se esse erro ocorrer no terminal PowerShell do VS Code, use
`$env:UV_LINK_MODE = "copy"` na sessão e rode `uv sync --locked` novamente.

Os testes cobrem a validade dos schemas, os exemplos sintéticos, campos
obrigatórios, UTC, versão, ambientes aceitos, versão do agregado e campos
opcionais. A expiração em relação ao relógio, a autorização, a idempotência e
a ordenação entre eventos serão verificadas nos componentes que usam os envelopes.
