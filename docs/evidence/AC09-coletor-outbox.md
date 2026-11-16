# AC09 — Coletor de métricas da Outbox

16/11/2026. Validação local no checkout oficial, base
`11e61c9a0875ed91ba68788063364f4dec44dfca` com as mudanças locais
AC07 e AC09. Python 3.12.12, PostgreSQL 17.11 descartável no Windows,
loopback, UTC, credenciais de teste, PAPER e TRAINING,
`LIVE_ENABLED=false`. [Hashes do código testado](AC09-outbox-metrics-sha256.txt)

## Uso

Após aplicar as migrações até `0017`, com o ambiente local configurado:

```powershell
uv run --no-sync python -m apps.event_dispatcher.metrics --window-seconds 300
```

O comando emite JSON com uma amostra por execução. Coletores podem
informar a janela em segundos. Os 300 segundos são o exemplo e
o valor de teste. A janela é inclusiva no início e exclusiva no fim.
A consulta usa o relógio UTC do PostgreSQL e transação somente
leitura em Repeatable Read. A classificação reutiliza o predicado
de ordenação do dispatcher. A idade usa `enqueued_at` e o atraso
reporta contagem, mínimo, p50, p95 e máximo. A migração `0017` cria
o histórico de tentativas. Cada par evento e número da tentativa
é único e gravado com a atualização da Outbox. O histórico começa
na migração. Eventos antigos podem contribuir para o atraso se
estiverem na janela, mas tentativas anteriores não são inferidas.

Fila vazia emite `status=ok`, backlog zero e idade nula.
Falha SQL emite `status=unavailable` sem contagens, e a CLI sai
com código 1. O JSON só dimensiona ambiente e condições fixas.

## Evidência

`python -m ruff check src infrastructure apps tests`,
`python -m ruff format --check src infrastructure apps tests`
e `python -m mypy` passaram. Com `RUN_POSTGRES_TESTS=1`,
`python -m pytest -q` resultou em **146 aprovados**.
`python -m apps.event_dispatcher.metrics --help` exibiu a janela
obrigatória. O teste `test_outbox_metrics_snapshot_and_transitions`
verificou os valores seguintes.

| Cenário | Esperado e confirmado |
|---|---|
| PAPER vazio | status ok e total zero |
| Após 5 falhas no mesmo evento e 1 retry de outro | Backlog total 4, um por condição. 6 tentativas, 5 retries e 1 falha terminal |
| Nova coleta na janela | Mesmos totais de transição, sem dupla contagem |
| Espera por retry | Idade igual ou superior a 30 s desde a entrada |
| Após duas publicações e reabertura da conexão | Backlog total 2. Duas observações de atraso com mínimo de 30 s. 8 tentativas, 5 retries e 1 falha terminal |
| Amostra TRAINING | Backlog e transições zero, segregados das transições de PAPER |
| Banco indisponível | JSON sanitizado abaixo, sem contagens |

```json
{"status":"unavailable","environment":"PAPER"}
```

Frequência, janela operacional, limiares, retenção do histórico,
tratamento de timestamps inconsistentes, responsáveis e duração
desde a detecção do bloqueio aguardam revisão humana. AC07 permanece
em revisão no seu próprio pacote. LIVE permanece indisponível.
O aceite técnico de AC09 e a decisão de G0 permanecem humanos.
