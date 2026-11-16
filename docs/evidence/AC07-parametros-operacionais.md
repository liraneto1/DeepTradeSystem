# AC07 — Parâmetros operacionais de escalonamento e retenção

16/11/2026. Base `11e61c9a0875ed91ba68788063364f4dec44dfca` com
alterações locais de AC07 e AC09. Validação em PostgreSQL 17.11
descartável, loopback, UTC, PAPER, credencial de teste e
`LIVE_ENABLED=false`. [Hashes do código testado](AC07-parametros-sha256.txt)

## Limiar

O dispatcher usa 3.600 segundos como valor inicial. Conta desde
`enqueued_at` do sucessor pelo relógio do PostgreSQL. Antes do
limiar o sucessor aguarda. A partir dele uma lacuna sem comprovante
abre quarentena. A remoção comprovada e a falha terminal abrem
quarentena sem esperar pelo limiar. A espera e o escalonamento
preservam as tentativas.

```powershell
uv run --no-sync python -m apps.event_dispatcher --gap-after-seconds 3600
```

Uma hora reaproveita o cenário já aprovado para o ensaio. O valor é
um ponto de partida para PAPER e TRAINING, até haver dados para rever o
tempo de espera aceitável. A CLI aceita um inteiro positivo.

## Retenção

Retenção mínima de 30 dias a partir de `published_at`, pelo relógio
do PostgreSQL. Adotei 30 dias como janela inicial conservadora para
investigação e recuperação no recorte local. Ao vencer a janela,
a remoção continua manual e depende de todos os critérios abaixo.

- Publicação e consumo confirmados.
- Agregado sem quarentena e sem versão posterior na Outbox.
- Decisão de retenção registrada. Antes de remover, a pessoa
  responsável confirma que o envelope original pode ser recuperado
  de fonte autoritativa.

`remove_published_event(engine, event_id, decision_reference=...)`
exclui a linha elegível e grava o comprovante na mesma transação.
Comprovantes, tentativas, marcadores de consumo e decisões de
quarentena são preservados. O prazo mínimo não aciona exclusão
automática. Se chegar uma nova versão depois da remoção, o
comprovante aciona quarentena. A retomada exige o envelope original
e uma decisão registrada.

A designação de responsáveis, a gestão de acesso à operação e a
confirmação da cardinalidade com produtores operacionais permanecem
na revisão de AC07. LIVE permanece indisponível e G0 segue aberto.

## Evidências

- Ruff e mypy passaram em 93 arquivos. A suíte PostgreSQL completa
  passou com 149 testes antes do cenário adicional de retenção.
- A rodada final direcionada passou com 3 testes e 42 desmarcados.
  O sucessor com 3.590 s aguardou. Com idade de 3.600 s, abriu
  incidente e manteve zero tentativas. A remoção comprovada abriu
  incidente sem esperar pela janela.
- Um evento recém-publicado e já consumido ficou protegido; aos
  30 dias sua remoção foi confirmada. Um evento com 31 dias ficou
  protegido antes do consumo e, depois do consumo, enquanto havia
  sucessor. Essas rejeições mantiveram as linhas e não criaram
  comprovantes.
- Comandos: `python -m pytest -q --tb=short` e
  `python -m pytest -q --tb=short tests/integration/test_postgres_migrations.py -k 'gap_escalation or outbox_retention'`,
  ambos com `RUN_POSTGRES_TESTS=1`.
