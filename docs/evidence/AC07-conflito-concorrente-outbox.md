# AC07 — Conflito concorrente de versão da Outbox

Base `11e61c9a0875ed91ba68788063364f4dec44dfca`, com migração
`0016`. Ensaio em PostgreSQL 17.11 descartável, loopback, UTC,
PAPER, `LIVE_ENABLED=false` e credencial de teste.

A pesquisa de chamadas a `append_event` e de inserções na Outbox
em apps, src, infraestrutura e testes encontrou somente a API de
gravação e fixtures. A cardinalidade de produtores operacionais
ainda precisa de confirmação. A regra de uma versão por escopo segue
o DOC-04 e é imposta por índice único, inclusive para conta ausente.
Se houver colisões existentes, a instalação do índice falha e a
migração reverte. A reconciliação de dados existentes requer decisão
humana antes de nova tentativa. Nenhuma linha é escolhida ou removida
automaticamente.

Ao receber a rejeição do índice, `append_event` registra o escopo,
o ID rejeitado, a versão, a correlação e a hora UTC por uma segunda
conexão. A tabela de incidentes não contém o payload. O commit da
auditoria é independente do rollback do produtor. O registro depende
de uma conexão disponível e do funcionamento do banco. Escritas diretas
via SQL recebem a restrição, e a trilha de auditoria passa por
`append_event`.

## Evidência

- `python -m ruff check src infrastructure apps tests` passou.
- `python -m mypy` passou em 86 arquivos.
- `RUN_POSTGRES_TESTS=1` e `python -m pytest -q` passaram com 145 testes.
- `test_concurrent_outbox_version_conflict_survives_rollback` abriu
  duas transações com mutações de estado e IDs diferentes para a mesma
  versão sem conta. Esperado e observado: um estado confirmado,
  um evento confirmado e um incidente persistente do evento rejeitado.
  O dispatcher publicou o vencedor e o evento da outra conta.

Cobertura desta entrega: colisão concorrente e durabilidade após
rollback. Quarentena do agregado, reparo autorizado, retomada após
reconciliação e confirmação com produtores continuam abertos em AC07.
AC09 aguarda seu pacote. LIVE permanece indisponível e G0 segue aberto.
