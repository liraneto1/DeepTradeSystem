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

## Exemplo de contrato
Ver `contracts/examples/command-envelope.example.json` e `event-envelope.example.json`.
