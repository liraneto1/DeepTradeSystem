# PostgreSQL 17 e migrations no VS Code

O PostgreSQL guarda o estado transacional do Trade System. O Alembic registra
qual revisão foi aplicada e executa a subida e a reversão das migrations.
A revisão `0001` cria o schema `trade_system`, onde ficarão os objetos da
aplicação. A tabela de controle do Alembic fica em `public.alembic_version`.

## Subir o banco local

Com Docker e Compose disponíveis, abra o terminal PowerShell do VS Code na
raiz do projeto e execute:

```powershell
uv sync --locked
$env:TRADE_SYSTEM_ENVIRONMENT = "PAPER"
$env:LIVE_ENABLED = "false"
$env:POSTGRES_PASSWORD = [guid]::NewGuid().ToString("N")
docker compose -f deploy/compose/postgres.yml up -d --wait
```

A porta padrão é `55432` e o banco escuta em `127.0.0.1`. Se a porta estiver
ocupada, defina `$env:POSTGRES_PORT` antes de subir o serviço. Use a mesma senha
ao reabrir um volume existente. Para mantê-la entre sessões, use um arquivo
local `.env` ignorado pelo Git e execute o Alembic com
`uv run --env-file .env alembic`.

Se o OneDrive bloquear hardlinks ou a atualização da `.venv`, configure
um ambiente virtual fora do OneDrive nesta sessão e repita `uv sync --locked
$env:TRADE_SYSTEM_ENVIRONMENT = "PAPER"
$env:LIVE_ENABLED = "false"`.

```powershell
$env:UV_LINK_MODE = "copy"
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:TEMP "deeptrade-venv"
```

## Reproduzir o teste em um banco descartável

Em um banco novo ou revertido até `base`, execute:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest tests/integration/test_postgres_migrations.py
Remove-Item Env:RUN_POSTGRES_TESTS
```

O teste verifica a versão do PostgreSQL, aplica `head`, confere o schema, a tabela Outbox e a
revisão gravada e reverte até `base` passando pela revisão `0001`. Ao final, a tabela de controle pode
continuar presente com zero revisões aplicadas.

Para aplicar e inspecionar manualmente:

```powershell
uv run --no-sync alembic upgrade head
uv run --no-sync alembic current
uv run --no-sync alembic downgrade base
docker compose -f deploy/compose/postgres.yml down
```

`down` preserva os dados do volume. Use `down --volumes` somente se você
quiser apagar os dados descartáveis desse projeto Compose.
