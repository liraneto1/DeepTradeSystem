# Isolamento e segredos no ambiente local

Defina a política do processo no terminal PowerShell do VS Code:

```powershell
$env:TRADE_SYSTEM_ENVIRONMENT = "PAPER"
$env:LIVE_ENABLED = "false"
```

Os únicos ambientes aceitos são `TRAINING` e `PAPER`. Use exatamente os
valores indicados. A ausência de qualquer uma dessas duas variáveis,
uma tentativa de selecionar `LIVE` ou um valor diferente de `false`
bloqueia a inicialização dos aplicativos e o acesso ao banco.

Defina `POSTGRES_PASSWORD` na sessão ou em um arquivo `.env` local,
ignorado pelo Git. Use `.env.example` como referência. Para carregar o
arquivo no processo Python, use `uv run --env-file .env` seguido do comando.
O Docker Compose lê o `.env` na raiz. O PostgreSQL usa `127.0.0.1` e a porta
`55432` por padrão. Uma porta informada deve estar entre 1 e 65535.
As respostas e mensagens de configuração omitem os valores secretos.

Com a política válida, a API de diagnóstico responde em `/health` e
`/info` mesmo quando o banco está indisponível. A prontidão retorna
`503` quando faltam credenciais ou a conexão falha. `/info` informa
`live_enabled: false`.

## Segregação dos eventos

Os aplicativos compartilham a instância PostgreSQL local. A separação é
lógica por `environment_id`: a Outbox e a publicação recusam eventos de
outro ambiente, e o dispatcher e o consumidor só selecionam mensagens do
ambiente configurado no processo. Use uma sessão por ambiente.

A revisão `0005` também impede novos registros com ambiente ausente ou
fora de `TRAINING` e `PAPER` na Outbox e na fila. A migration preserva os
registros existentes. Mensagens antigas fora da política ficam fora da
seleção dos workers.
