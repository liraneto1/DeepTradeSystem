# AC07 — Autorização para remoção e retomada

16/11/2026. Base `11e61c9a0875ed91ba68788063364f4dec44dfca` com
alterações locais de AC07 e AC09. Validação em PostgreSQL 17.11
descartável, loopback, UTC, PAPER, credenciais de teste e
`LIVE_ENABLED=false`. [Hashes do código testado](AC07-autorizacao-sha256.txt)

## Responsabilidades

| Operação | Responsável funcional | Papel PostgreSQL |
|---|---|---|
| Remoção por retenção | Operações de Dados, após verificar a elegibilidade e a fonte autoritativa | `outbox_retention_authorizer` |
| Retomada após reconciliação | Operações da Outbox, após conferir a cadeia e os efeitos publicados | `outbox_resume_authorizer` |

A migração `0020` cria papéis de grupo sem login. O administrador
atribui cada papel a um login individual designado. Os papéis
são distintos e o dispatcher cotidiano segue sem associação.
Exemplo de provisionamento, com nomes ilustrativos de logins existentes:

```sql
GRANT outbox_retention_authorizer TO operador_dados;
GRANT outbox_resume_authorizer TO operador_outbox;
```

A verificação em PostgreSQL usa `session_user` e associações
herdáveis explícitas. A referência da decisão complementa a
identidade autenticada. A migração preserva autoria nula em
decisões antigas, cuja identidade não foi registrada. As operações
novas gravam `removed_by` no comprovante e `released_by` no
incidente. Use `remove_published_event` e `release_quarantine`
para executar as verificações operacionais e gravar a decisão.

Os papéis têm acesso às tabelas necessárias para as operações.
Os gatilhos barram exclusão da Outbox e alterações de liberação
por identidades sem associação ao papel correspondente. Membros
autorizados têm privilégios SQL para executar o fluxo, portanto
o procedimento operacional exige usar as APIs que preservam o
comprovante e reconciliam a cadeia. A administração privilegiada
do cluster mantém capacidade de alterar privilégios e esquema.
Para operação segregada, os processos cotidianos devem usar
logins sem privilégios administrativos.

A atribuição nominal a logins existentes permanece sob decisão do
administrador responsável. Nenhum login real foi provisionado neste
ensaio. LIVE permanece indisponível e G0 segue aberto.

## Evidências

- `python -m pytest -q --tb=short`, com `RUN_POSTGRES_TESTS=1`,
  passou com 151 testes. Ruff, formatação e mypy passaram.
- `test_outbox_sensitive_operations_require_database_membership`
  usou três identidades PostgreSQL por `SET SESSION AUTHORIZATION`
  em conexões separadas, a partir do administrador de testes.
- A identidade de diagnóstico e a identidade de retomada receberam
  SQLSTATE 42501 ao tentar remoção. A identidade de diagnóstico
  também recebeu rejeição no DELETE direto, mesmo com esse grant.
- A identidade de diagnóstico e a identidade de retenção receberam
  rejeição na retomada. As respectivas operações autorizadas
  gravaram `ac07_data_operator` e `ac07_dispatch_operator` no banco,
  com as referências de decisão do ensaio.
