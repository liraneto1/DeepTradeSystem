# TS-ADR-093 — Transactional Outbox e consumidores idempotentes

- **Estado da ficha:** APPROVED
- **Aprovação da ficha:** 17/11/2026, revisão e aprovação comunicadas pelo usuário nesta conversa.
- **Estado da decisão de origem:** APPROVED
- **Domínio:** Engenharia I00 (transversal)
- **Baseline de origem:** V1.0
- **Data de elaboração:** 17/11/2026

## Decisão registrada

Transactional Outbox e consumidores idempotentes

## Proveniência

- [Fonte primária](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>). Registro consolidado na linha 848.
- [Índice de reconciliação](<../governance/ADR-RECONCILIATION.md>). Título e referências de apoio.
- SHA-256 da fonte primária: CF344917FB21C598DB9F17A535D4BF1CA15116874F109612DBCD9B191883DF29.

## Contexto, alternativas e consequências

O Engineering Foundation contém uma ficha histórica com contexto, alternativas e consequências nas linhas 634–646, em estado PROPOSED. A aprovação posterior está registrada na linha 848.

> ### ADR de referência — TS-ADR-093
> 
> Transactional Outbox como mecanismo inicial de eventos
> Domínios D05/D06 · Estado: PROPOSED
> 
> Contexto: os fluxos críticos exigem consistência entre persistência de estados e emissão de eventos.
> 
> Decisão: registrar mudanças de estado e mensagens Outbox na mesma transação PostgreSQL. Um dispatcher separado publicará os eventos para consumidores idempotentes.
> 
> Consequências: reduz a complexidade inicial, mas exige controle de retries, concorrência, ordenação por agregado, checkpoints e monitoramento.
> 
> Alternativas: Kafka, RabbitMQ ou publicação direta após commit. Permanecem opções futuras mediante necessidade comprovada.
> 

## Rastreabilidade pendente

Responsável nominal, dependências e vínculos individuais com outros artefatos aguardam conferência documental.