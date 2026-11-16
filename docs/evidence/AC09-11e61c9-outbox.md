# AC09 — Ensaio de métricas da Outbox

16/11/2026. Candidato `11e61c9a0875ed91ba68788063364f4dec44dfca`.
PostgreSQL 17.11 descartável no Windows, loopback, UTC, credencial de
teste, PAPER e TRAINING, `LIVE_ENABLED=false`.

A sonda `python -` executou `alembic upgrade head`, gravou dados
sintéticos via `append_event` e acionou `dispatch_once`. Cada amostra
usou uma transação Repeatable Read, `transaction_timestamp()` e o
predicado de predecessor do dispatcher. A idade partiu de
`enqueued_at` e o atraso usou `published_at - enqueued_at`.
O ensaio conferiu as medidas com uma consulta de referência.

| Cenário | Esperado | Observado |
|---|---|---|
| PAPER vazio | Total 0 | 0 |
| Após publicação e retry em PAPER | Total 3, um bloqueado, um retido e um em espera. Idade e atraso de pelo menos 30 s | Três grupos com uma linha cada, 30,014901 s de idade e atraso de 30,011281 s |
| Após sucesso do retry | Total 2, um bloqueado e um retido. Duas observações de atraso | Idades de 30,022436 s. Atrasos de 30,011281 s e 30,021764 s |
| TRAINING no mesmo banco | Um elegível, isolado do dispatcher PAPER | Um elegível |
| Conexão reaberta | Categorias preservadas | Categorias preservadas |
| Porta descartável sem serviço | Coleta indisponível distinguível de zero | OperationalError, fila vazia devolveu zero |

No fixture, o sucessor do evento retido tinha disponibilidade futura.
A classificação observada foi bloqueado, confirmando a precedência.
O evento de retry preservou sua idade e o teste antecipou a
disponibilidade no banco para verificar a publicação.

Log sanitizado da transição observada:

```json
{"event":"outbox_retry_scheduled","environment_id":"PAPER","attempt":1,"retry_delay_seconds":1,"error_type":"ConnectionError"}
```

Ainda faltam o coletor de métricas do produto, a publicação do estado
de indisponibilidade, a distribuição com janela explícita e as
contagens deduplicadas de tentativas, retries e falhas por intervalo.
A sonda usou o histórico sintético inteiro para medir atraso.
Frequência, janela, limiares, relógio para alertas e responsáveis
aguardam revisão humana. Engenharia e QA devem repetir a validação
sobre a implementação do coletor. AC09 permanece parcial.
