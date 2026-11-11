# 03 — Contratos iniciais e invariantes

## CommandEnvelope v1 — proposta física aprovada conceitualmente
Campos: `command_id`, `command_type`, `schema_version`, `idempotency_key`, `correlation_id`, `environment_id`, `account_id`, `issued_at`, `expires_at`, `actor`, `authorization_ref` (quando aplicável), `payload`.

## EventEnvelope v1
Campos: `event_id`, `event_type`, `schema_version`, `correlation_id`, `causation_id`, `aggregate_type`, `aggregate_id`, `aggregate_version`, `environment_id`, `account_id` (quando aplicável), `event_time`, `recorded_at`, `producer`, `payload`.

## Contratos complementares propostos
`ErrorEnvelope.v1`, `HealthStatus.v1`, `OutboxRecord.v1` e API de health/readiness/system info. Definições exatas e compatibilidade devem ser testadas; exemplos não são JSON Schemas definitivos.

## Invariantes
- Idempotência por chave e escopo; `event_id` único.
- Ordenação por agregado, `aggregate_version` monotônica.
- UTC para timestamps; `event_time`, `received_at`, `available_at` nos dados de mercado futuros.
- Valores monetários e quantidades como decimal string, não float.
- Estado e Outbox na mesma transação; consumidores idempotentes.
- Comandos expiram; identidade/ambiente/escopo e autorização são validados.
- UNKNOWN em execução financeira futura implica reconciliação antes de qualquer reenvio.
- No I00, usar somente eventos sintéticos e nunca endpoints reais de ordens.

## Schemas e exemplos do I00-03

| Envelope | Schema JSON 2020-12 | Exemplo sintético |
|---|---|---|
| Comando | [CommandEnvelope v1](../contracts/jsonschema/command-envelope.v1.schema.json) | [Comando de diagnóstico](../contracts/examples/command-envelope.example.json) |
| Evento | [EventEnvelope v1](../contracts/jsonschema/event-envelope.v1.schema.json) | [Evento de diagnóstico](../contracts/examples/event-envelope.example.json) |

O schema define os campos obrigatórios e aceita a versão `1.0.0`. Identificadores
são strings com ao menos um caractere diferente de espaço em branco. Os ambientes
aceitos são `TRAINING` e `PAPER`. Datas usam RFC 3339 em UTC com sufixo `Z`
ou `+00:00`. Ative a verificação de formato no validador JSON Schema para
conferir o calendário e o horário.

`authorization_ref` no comando e `account_id` no evento podem ser omitidos.
Quando presentes, seguem o mesmo formato dos demais identificadores.
`aggregate_version` começa em 1. Cada tipo de mensagem poderá definir seu
próprio schema de `payload`. Tipos com valores monetários ou quantidades
deverão declará-los como strings decimais.

A validade temporal do comando, a autorização do ator, a unicidade dos IDs e
a progressão da versão do agregado dependem de relógio, contexto ou estado
persistido. Os schemas validam a forma de cada mensagem individual.

Para reproduzir os testes no terminal do VS Code, execute
`uv sync --locked` e `uv run --no-sync pytest tests/contracts`.
