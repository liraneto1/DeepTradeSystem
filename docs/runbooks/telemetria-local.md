# Telemetria local no VS Code

Cada linha de log da aplicação é um objeto JSON. O campo `correlation_id`
é a chave para acompanhar uma solicitação ou evento em processos diferentes.
Os campos `trace_id` e `span_id` identificam a operação instrumentada pelo
OpenTelemetry dentro do processo. A correlação entre processos usa o
`correlation_id` do envelope. Nenhum exportador está configurado no I00.

## Consultar a API pelo ID de correlação

Configure o ambiente conforme o [guia de isolamento](isolamento-e-segredos.md).
Na raiz do repositório, inicie a API em um terminal do VS Code:

```powershell
uv run --no-sync python -m apps.api
```

Em outro terminal:

```powershell
curl.exe -i -H "X-Correlation-ID: corr_example" http://127.0.0.1:8000/health
```

A resposta inclui `X-Correlation-ID`. A API gera um ID quando o valor
enviado está ausente ou fora do formato aceito. Procure `corr_example` no
terminal da API. Para testar toda a cadeia com um evento sintético, siga
a configuração do [PostgreSQL](postgresql-local.md), use um banco
descartável em `base` e rode:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest tests/integration -k correlation
Remove-Item Env:RUN_POSTGRES_TESTS
```

## Campos registrados

Os registros incluem horário UTC, nível, componente e operação. A API
inclui o nome da rota e o status HTTP. Dispatcher e consumidor incluem
os IDs do evento e da causa, quando disponíveis, e o ambiente. O
dispatcher registra tentativas e atrasos de retry.

A aplicação grava somente os campos autorizados. Payloads, query strings,
cabeçalhos brutos, senhas, parâmetros SQL e mensagens de exceção ficam
fora dos registros. A entrada `python -m apps.api` desativa o log de
acesso padrão do Uvicorn, que poderia incluir a URL completa.
