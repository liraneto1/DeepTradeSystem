# AC07 — Escalonamento de predecessor ausente ou removido

16/11/2026. Base `11e61c9a0875ed91ba68788063364f4dec44dfca` com
alterações locais de AC07 e AC09. PostgreSQL 17.11 descartável
em loopback, UTC, PAPER, credenciais de teste e `LIVE_ENABLED=false`.

A revisão `0019` registra o motivo e a versão esperada no incidente.
O dispatcher revalida a lacuna do predecessor imediato sob o bloqueio
do agregado. O escalonamento grava uma quarentena sem invocar o
publicador ou alterar tentativas do sucessor. Uma lacuna sem comprovante
usa a idade desde a entrada do sucessor. A retenção comprovada é
escalonada sem esperar pelo limiar.

A remoção explícita por `remove_published_event` exige decisão de
retenção, publicação e marcador de consumo. A exclusão e o comprovante
são confirmados na mesma transação. O comprovante inclui o hash do
envelope e o contador original de tentativas. A retomada requer repor o evento original e validar seu hash.
A migração recusa downgrade com incidentes novos ou comprovantes.

Exemplo de configuração local de ensaio, usando 3.600 segundos:

```powershell
uv run --no-sync python -m apps.event_dispatcher --gap-after-seconds 3600
```

Sem a opção, lacunas sem comprovante continuam aguardando.
Remoções históricas ou manuais sem comprovante são tratadas como
lacunas sem origem comprovada. O limiar operacional, a política de
retenção e a autoridade para registrar a decisão continuam sujeitos à
revisão humana. LIVE permanece indisponível e G0 segue aberto.

## Evidência

- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q --tb=short`
  passou com 149 testes. Ruff, formatação e mypy passaram.
- Sem predecessor, a fila aguardou antes do limiar de uma hora.
  Com duas horas de idade sintética, gravou motivo `missing` e
  versão esperada 1.
- Após remover a versão 1 publicada e consumida pela API de
  retenção, o dispatcher gravou `retention_removed` e versão
  esperada 1, mesmo sem limiar configurado.
- Nos dois casos, o sucessor manteve zero tentativas e nenhuma
  publicação durante a quarentena. Reabrir a conexão e repetir
  a varredura manteve um incidente. Outro agregado publicou.
- A liberação falhou com a cadeia incompleta. Após repor o
  envelope original, o agregado continuou bloqueado até registrar
  a decisão de liberação. A projeção terminou com três efeitos
  para três IDs únicos, inclusive quando a versão 1 foi reenviada.
- [Hashes do código e lockfile testados](AC07-escalonamento-sha256.txt)
