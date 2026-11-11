# Evidências de I00-13

Validação local em 11/11/2026 com Windows x64, Python 3.12.12 e uv 0.9.26.
A entrega segue TS-ADR-093 e TS-ADR-094 e cobre cenários de I00-AC07 e
I00-AC08 no fluxo sintético local.

| Cenário em PostgreSQL 17 | Condição verificada |
|---|---|
| Versão 2 chega antes da versão 1 | Fica pendente sem consumir tentativas. Outro agregado avança. Após a chegada da versão 1, as entregas saem na ordem 1, 2. |
| Publicador temporariamente indisponível | A primeira tentativa agenda retry e deixa a fila vazia. Após o prazo simulado pelo teste, a segunda tentativa grava uma entrega e marca o evento como publicado. |
| Workers sem acesso ao PostgreSQL | Cada processo falha ao conectar a uma porta local sem serviço. Com o endereço correto, novos processos retomam a publicação e o consumo. A entrega pendente produz um único incremento. |
| Interrupção após publicar e antes de confirmar a Outbox | O teste de regressão verifica republicação. O teste do consumidor verifica que duas entregas do mesmo evento produzem um efeito. |
| Falhas persistentes ou após aplicar o efeito | Os testes de regressão verificam retenção após o limite de tentativas e rollback do efeito, da deduplicação e da confirmação. |

O teste de conexão usa processos reais em uma porta sem serviço. O
PostgreSQL do CI continua ativo, permitindo verificar que os dados
pendentes foram preservados. O teste de retry altera a disponibilidade
no banco para exercitar a retomada sem esperar pelo relógio.

| Verificação local | Resultado |
|---|---|
| `uv run --no-sync ruff check src infrastructure apps tests` | Sem violações. |
| `uv run --no-sync ruff format --check src infrastructure apps tests` | 44 arquivos formatados. |
| `uv run --no-sync mypy` | Sem erros em 44 arquivos-fonte. |
| `uv run --no-sync pytest` | 69 testes passaram. Dezesseis testes com PostgreSQL ficaram para o CI. |
| `uv build --no-sources` | Wheel e distribuição fonte gerados. |

Veja o [guia do dispatcher](../runbooks/dispatcher-outbox.md) para reproduzir
os testes. O bloqueio cobre lacunas de versão no fluxo pela Outbox. A
reconciliação de versões conflitantes ou lacunas permanentes continua
pendente no [registro mestre](../backlog/registro-mestre-i00.md).
