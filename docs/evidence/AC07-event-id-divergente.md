# AC07 — Reutilização de event_id na Outbox

Base `11e61c9a0875ed91ba68788063364f4dec44dfca` com as mudanças
locais de AC07 e AC09. PostgreSQL 17.11 descartável em loopback,
UTC, PAPER, credencial de teste e `LIVE_ENABLED=false`.
[Hashes do código validado](AC07-event-id-sha256.txt)

A revisão `0022` registra incidentes de reutilização divergente do
mesmo ID. A Outbox compara o envelope integral em JSONB. Diferenças
na ordem de chaves de objeto são equivalentes. Um replay equivalente
reverte a transação repetida e preserva o evento original sem abrir
incidente. O consumidor mantém o efeito único para a mesma identidade.

Para divergência, a transação do produtor reverte antes da gravação
independente do incidente e da quarentena do agregado original.
A evidência inclui ID, hashes SHA-256, ambiente e correlação
da tentativa, sem payload. Para IDs que saíram por retenção,
o comprovante fornece o escopo e o hash do envelope original.
A restauração usa o hash persistido.

## Evidência

- Ruff, formatação e mypy passaram em 96 arquivos.
- `RUN_POSTGRES_TESTS=1` e `python -m pytest -q --tb=short`
  passaram com 153 testes.
- Após acrescentar as duas verificações de incidente ausente e
  tentativas do sucessor, a rodada direcionada passou com 5 testes
  e 43 desmarcados. Filtro `event_id_divergence or
  concurrent_outbox_version or duplicate_event or gap_escalation`.
- O teste registrou uma mutação original. Mutações de replay
  equivalente e divergente foram revertidas. O incidente permaneceu
  com dois hashes distintos. A quarentena bloqueou a versão 2 com
  zero tentativas. Reenviar o envelope equivalente ao consumidor
  preservou um marcador de consumo e um efeito de projeção.

A detecção de divergência descrita nesta entrega ocorre na API
transacional da Outbox. O ensaio cobre o dispatcher e o consumidor
local. O aceite técnico permanece sujeito à revisão humana.
LIVE permanece indisponível e G0 segue aberto.
