# Evidências do bootstrap I00

Validação local em 11/11/2026, Windows x64, CPython 3.12.12 e uv 0.9.26.
As alterações foram validadas no checkout local `codex/i00-bootstrap`,
antes do primeiro commit. Baselines `TS-ARCH-GLOBAL-V1.0` e `TS-ENG-I00-V1.0`.

| Pacote | Decisões | Resultado e aceite |
|---|---|---|
| I00-01 | TS-ADR-089, 090, 098 | Instalação local e imports verificados. Os pacotes contêm somente a estrutura inicial, sem serviços de execução ou acesso LIVE. |
| I00-02 | TS-ADR-094 | Lockfile consistente, instalação com `--locked`, lint, formatação, tipos, testes e build aprovados localmente. |
| I00-11 | TS-ADR-095 | Workflow configurado para push e pull request. Aceite de workflow verde pendente de execução no GitHub. |

## Resultados observados

| Comando ou verificação | Resultado |
|---|---|
| Comparação dos arquivos extraídos com o ZIP | 21 entradas conferidas. O README mantém o conteúdo original e inclui uma seção adicional. |
| `uv python install 3.12` | CPython 3.12.12 instalado. |
| `uv lock` e `uv lock --check` | 15 pacotes resolvidos e lockfile consistente. |
| `uv sync --locked` | 15 pacotes instalados, incluindo o projeto. |
| `uv run --no-sync ruff check .` | Sem violações. |
| `uv run --no-sync ruff format --check .` | 24 arquivos já formatados. |
| `uv run --no-sync mypy` | Sem erros em 13 arquivos-fonte. |
| `uv run --no-sync pytest` | 11 testes de importação passaram. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. O pacote raiz e os 11 módulos foram importados diretamente do wheel com Python em modo isolado. |

## SHA-256

- `uv.lock` — `9d05441bc5cd3f0c05dfc3b28361569b1a07347ddd4d4e7498a1039cd0ceffa5`
- `deep_trade_system-0.1.0-py3-none-any.whl` — `2f1fe9df21b69f8e2b7a4dd078a9bc122b011f1a042391e481551ff91963947d`
- `deep_trade_system-0.1.0.tar.gz` — `6e679ff554999fe040f8ff54d7f9ca94e0ef69c56cfe6da29740f0efeb9a72d1`

## Pendências

A execução em Linux e o status do GitHub Actions ainda precisam ser verificados.
Os hashes identificam os artefatos deste build local. O aceite integral de I00 e
a decisão sobre G0 seguem pendentes. Contratos, PostgreSQL e Outbox aguardam
aprovação antes da implementação.

## Primeira execução do GitHub Actions

A [execução do commit de bootstrap](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43068400012)
instalou Python e as dependências do lockfile e passou no lint. A checagem de
formatação percorreu a raiz e encontrou o `Teste.py` do commit anterior ao
bootstrap. O README e o workflow passaram a verificar `src` e `tests`, os
diretórios Python entregues neste pacote.
