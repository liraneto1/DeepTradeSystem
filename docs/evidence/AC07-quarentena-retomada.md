# AC07 — Quarentena durável e retomada da Outbox

16/11/2026. Base `11e61c9a0875ed91ba68788063364f4dec44dfca` com
mudanças locais de AC07 e AC09. PostgreSQL 17.11 descartável,
loopback, UTC, PAPER, `LIVE_ENABLED=false` e credenciais de teste.
[Identidade dos arquivos testados](AC07-quarentena-sha256.txt)

A migração `0018` registra quarentenas por ambiente, conta, tipo e
ID do agregado. Migra incidentes de colisão e eventos já retidos.
Novos conflitos gravados por `append_event` registram a quarentena
na transação de auditoria. O dispatcher abre quarentena com a
falha terminal. O bloqueio é compartilhado com as métricas de AC09.
O dispatcher confirma o escopo sob bloqueio transacional antes
de publicar, e a liberação serializa no mesmo escopo.

Para reconciliar, confirme a fonte autoritativa e reponha o evento
original faltante pela API transacional da Outbox. Aplique a decisão
humana por `release_quarantine(engine, aggregate, decision_reference=...)`.
A API confere cadeia contínua desde a versão 1 e marcadores do
consumidor local para o prefixo publicado. A decisão e o horário
ficam persistidos. Eventos retidos elegíveis voltam à fila com as
tentativas anteriores preservadas. Chamadas repetidas após a
liberação retornam zero.

## Evidência

- `python -m pytest -q` com `RUN_POSTGRES_TESTS=1` passou com 147 testes.
- Após adicionar a verificação explícita de efeito ainda não consumido,
  a execução direcionada de quarentena, concorrência, métricas e
  retenção passou com 4 testes e 38 desmarcados.
- Ruff e mypy passaram. Formatação conferida em 91 arquivos.
- Conflito detectado após publicar v1. Após reabrir a conexão, a
  quarentena continuou ativa e o agregado independente foi publicado.
  A liberação falhou com efeito ainda não consumido e depois com
  lacuna de v2. O reparo de v2 deixou zero tentativas até a liberação.
- Após o reparo e outra abertura da conexão, a liberação registrou a
  referência de decisão. Ordem observada de retomada: v2, v3.
  Após reenvio de v1, a projeção permaneceu em quatro efeitos para
  quatro IDs únicos. A liberação repetida não criou nova decisão.

A referência de decisão é registrada por quem tem acesso local
à API Python. A designação e o controle operacional de quem pode
autorizar a retomada continuam sob revisão humana. A cadeia exige
histórico desde v1. Se a retenção removeu um predecessor, a liberação
depende de reconciliação e restauração da cadeia. O limiar para
escalonar lacunas e a confirmação da cardinalidade com produtores
operacionais permanecem pendentes. LIVE permanece indisponível e
G0 segue aberto.
