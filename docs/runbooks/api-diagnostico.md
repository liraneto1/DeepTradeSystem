# API local de diagnóstico no VS Code

No terminal PowerShell do VS Code, na raiz do repositório:

```powershell
uv sync --locked
$env:TRADE_SYSTEM_ENVIRONMENT = "PAPER"
$env:LIVE_ENABLED = "false"
uv run --no-sync python -m apps.api
```

Em outro terminal, consulte a API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/info
curl.exe -i http://127.0.0.1:8000/readiness
```

| Endpoint | Resposta |
|---|---|
| `GET /health` | `200` com `status: ok` se a API estiver respondendo. |
| `GET /readiness` | `200` com `status: ready` se o PostgreSQL responder e estiver na revisão atual do Alembic. Caso contrário, retorna `503` com `status: not_ready` e o estado de cada verificação. |
| `GET /info` | `200` com o nome e a versão do serviço e `live_enabled: false`. |
| `GET /openapi.json` | Especificação dos endpoints e modelos de resposta. |

Para obter prontidão, inicie o [PostgreSQL local](postgresql-local.md),
execute `uv run --no-sync alembic upgrade head` e inicie o servidor
na sessão que tem a configuração do banco. Se você iniciou o servidor
em outra sessão, reinicie-o com as variáveis do PostgreSQL disponíveis.

A API é somente leitura. A verificação de prontidão consulta o banco e
o histórico de migrations. As respostas omitem a URL do banco, a senha e
o texto de erros internos. Use **Ctrl+C** para encerrar o servidor.
