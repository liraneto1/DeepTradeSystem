# Prompt para iniciar no Codex

Você está trabalhando no repositório DeepTradeSystem, projeto TRADE SYSTEM V1. Leia primeiro `AGENTS.md` e todos os documentos `docs/00` a `docs/06`. A arquitetura global `TS-ARCH-GLOBAL-V1.0` e a baseline técnica `TS-ENG-I00-V1.0` estão aprovadas. **LIVE é proibido**.

**Primeira tarefa, exclusivamente:** implementar I00-01 (bootstrap monorepo), I00-02 (toolchain Python) e I00-11 (CI inicial), respeitando as ADRs TS-ADR-089–098. Antes de editar, examine o repositório e apresente um plano com arquivos afetados e eventuais conflitos. Não sobrescreva arquivos existentes sem revisão. Crie estrutura de pacotes Python, `pyproject.toml`, lockfile, Ruff/mypy/pytest, testes de smoke, `.env.example` sem segredos, `.gitignore`, Docker Compose mínimo somente para infraestrutura de desenvolvimento quando necessário, e GitHub Actions. Não implementar Binance, PPO, Risk/Execution operacionais, nem endpoints financeiros.

Ao terminar, execute os testes disponíveis, apresente comandos e resultados reais, liste arquivos criados/alterados, pendências, riscos e critérios de aceite atendidos. Não faça push/deploy sem autorização. Aguarde validação antes de avançar a I00-03.
