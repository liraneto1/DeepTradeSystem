# AC07 — Ensaio de ordenação da Outbox

16/11/2026. Candidato `11e61c9a0875ed91ba68788063364f4dec44dfca`.
PostgreSQL 17.11 descartável no Windows, loopback, UTC, credencial de
teste, PAPER, `LIVE_ENABLED=false` e `RUN_POSTGRES_TESTS=1`.

```powershell
python -m pytest -q tests/integration/test_postgres_migrations.py -k 'out_of_order_arrival or dispatcher_orders or dispatcher_retries_then_retains or dispatcher_retry_recovers or duplicate_event or duplicate_deliveries or consumer_rolls_back or correlation_traces'
```

Resultado: 8 aprovados e 31 desmarcados. Os testes confirmaram espera
por predecessor, progresso independente, publicação em ordem após
chegada tardia, retry, retenção, rollback e efeito único no replay.

Uma sonda com `python -` migrou o banco vazio até head. Dois escritores
em transações distintas chamaram `append_event` com IDs sintéticos
distintos, mesmo agregado, versão e ambiente, sem conta. Uma barreira
sincronizou as transações antes do commit. Em seguida o dispatcher
publicou até esvaziar a fila.

```text
AC07 concurrent_same_version expected=1_row_conflict observed=2_committed,2_published
```

O candidato garante unicidade de event_id. O conflito de versão
concorrente é um requisito aberto. A busca por `append_event` em
apps, src, infraestrutura e testes encontrou a definição e chamadas
de teste. A cardinalidade de produtores operacionais continua sem
confirmação.

Faltam estratégia para dados existentes, persistência de evidência de
conflito após rollback, incidente auditável, teste de predecessor
removido, reparo com reinício e retomada autorizada após conflito já
publicado. Engenharia precisa confirmar cardinalidade com produtores
e propor o caminho durável. QA deve validar os cenários faltantes.
Governança deve designar fonte autoritativa, responsáveis, limiar e
retenção. AC07 fica aberto para revisão humana.
