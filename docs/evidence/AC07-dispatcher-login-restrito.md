# AC07 — Dispatcher com login PostgreSQL restrito

16/11/2026. Base `11e61c9a0875ed91ba68788063364f4dec44dfca` com
alterações locais de AC07 e AC09. PostgreSQL 17.11 descartável,
loopback, UTC, PAPER, `LIVE_ENABLED=false` e credenciais de teste
geradas no ensaio. [Hashes do código testado](AC07-dispatcher-login-sha256.txt)

A revisão `0021` cria o papel de grupo `outbox_dispatcher_worker`.
O papel lê os dados necessários à seleção e aos bloqueios, atualiza
o estado de publicação e grava entregas, tentativas e incidentes.
As colunas de liberação, exclusão de eventos e as funções de
autorização de retenção e retomada continuam sujeitas aos papéis de
AC07. A CLI exige as variáveis de credencial dedicadas e valida
os privilégios do login antes de processar eventos.
[Guia do dispatcher](../runbooks/dispatcher-outbox.md)

O login de teste autenticou por SCRAM como `ac07_dispatcher_login`,
com todos os atributos administrativos testados desativados e
associação exclusiva ao papel de dispatcher. O teste usa um login
efetivo, aberto com senha própria no banco descartável.

Nenhum login operacional foi provisionado. O administrador do
banco atribui o papel em ambientes reais. LIVE permanece
indisponível e G0 segue aberto.

## Resultados

- `RUN_POSTGRES_TESTS=1` e `python -m pytest -q --tb=short`
  passaram com 152 testes. Ruff, formatação e mypy passaram.
- A CLI rejeitou o login administrativo com `ConfigurationError`
  e, com o login restrito, registrou `outbox_published`. O ensaio
  também verificou recuperação após indisponibilidade do banco.
- O login restrito gravou uma entrega. A Outbox mostrou uma tentativa
  e `published_at` preenchido.
- O mesmo login recebeu `operation not authorized` ao chamar as
  APIs de remoção e liberação. DELETE direto e UPDATE direto de
  `released_at` retornaram SQLSTATE `42501`. Ao final, a quarentena
  seguia ativa e a tabela de comprovantes estava vazia.
- O primeiro ensaio detectou leitura implícita do ID da entrega
  durante o INSERT. O publicador passou a inserir sem retornar
  esse ID. O grant permaneceu limitado à inserção.
