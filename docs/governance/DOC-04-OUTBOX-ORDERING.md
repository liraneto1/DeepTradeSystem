# DOC-04 Ordenação e reconciliação da Outbox

**16/11/2026 · APPROVED · proposta aprovada pelo usuário nesta conversa.** Recorte de P51, TS-ST-004, I00-06/07/13 e I00-AC07/08. A proposta preserva a Outbox transacional e a entrega ao menos uma vez de ADR-044/045 e TS-ADR-093. G0 segue aberto. LIVE permanece indisponível.

[Contratos e invariantes](../03-CONTRATOS.md) · [Matriz I00](DOC-03-I00-TRACEABILITY.md)

## Decisões aprovadas e parâmetros a definir

1. **Identidade e conflito.** Aprovar um evento por versão no escopo ambiente, conta, tipo e ID do agregado, condicionado à confirmação dos produtores. Aprovar que dois IDs distintos na mesma versão constituam conflito e que o mesmo ID com conteúdo divergente gere incidente. A comparação de conteúdo e o tratamento dos registros legados serão detalhados por Engenharia.
2. **Bloqueio e escalonamento.** Aprovar a espera pelo predecessor sem consumir tentativas e o bloqueio apenas do agregado afetado. Um predecessor retido ou espera acima do limiar aprovado abre incidente. Definir quem aprova o limiar e a retenção após os ensaios de Engenharia e QA.
3. **Reparo e retomada.** Aprovar a recuperação a partir de fonte autoritativa, com histórico preservado e decisão humana para correções excepcionais. A liberação depende de cadeia reconciliada e efeito único. Designar quem autoriza a retomada.

## Evidência de Engenharia para fechar AC07

| Cenário | Critério verificável |
|---|---|
| Duplicidade e conflito | Replay equivalente preserva efeito único. Inserções concorrentes de IDs distintos na mesma versão detectam conflito e preservam evidência mesmo após rollback. Ambiente e conta, inclusive conta ausente, são tratados no escopo correto. |
| Predecessor ausente, retido ou removido pela retenção | Sucessores ficam bloqueados sem gastar tentativas por falta de predecessor. O incidente é identificável, o bloqueio sobrevive a reinício e agregados independentes avançam. Demonstrar também chegada tardia e ordem de publicação. |
| Reparo e conflito após publicação | Reconciliar efeitos anteriores, testar reinício durante o reparo e demonstrar retomada auditável sem saltos de versão ou efeitos duplicados. |

Anexar ao candidato os cenários PostgreSQL, estado esperado e observado, logs sanitizados e resultado de QA. Reproduzir em ambiente local isolado de TRAINING ou PAPER com LIVE_ENABLED=false. Os testes históricos abaixo são ponto de partida.

## Comportamento observado

O dispatcher separa agregados por ambiente, conta, tipo e ID. Trata a conta ausente como parte do escopo. Uma versão acima de 1 só avança quando o predecessor imediato está publicado e não há versão anterior sem publicação. Um predecessor retido após falhas continua bloqueando as versões seguintes. Uma lacuna pode esperar sem consumir tentativas de publicação. A chave da tabela garante unicidade de event_id. O seletor usa versões estritamente menores para bloquear o avanço e não resolve duas linhas com IDs distintos na mesma versão. [Dispatcher](../../infrastructure/events/dispatcher.py) · [Outbox](../../infrastructure/events/outbox.py)

## Política proposta

| Situação | Tratamento proposto |
|---|---|
| Repetição de evento | O mesmo event_id com conteúdo equivalente é replay. Preservar o efeito único e a evidência original. A inserção duplicada hoje pode reverter a transação. Qualquer tratamento idempotente no produtor deve impedir uma segunda mutação de estado. O mesmo ID com conteúdo divergente exige incidente. |
| Versão conflitante | Para um mesmo escopo de agregado, tratar IDs distintos reivindicando a mesma versão como conflito, mesmo com payload equivalente. Validar a premissa de um evento por versão com os produtores. Proteger a identidade de versão no momento da gravação, inclusive sob concorrência e conta ausente. Se a disputa for detectada após publicação, bloquear o avanço e reconciliar também os efeitos já aplicados. Preservar os registros e a evidência do conflito. |
| Lacuna recuperável | Aguardar o predecessor sem consumir tentativas de publicação. Manter os sucessores pendentes e permitir progresso dos agregados independentes. Medir a idade do bloqueio separadamente das falhas de entrega. |
| Suspeita de lacuna permanente | Ao atingir o limiar aprovado ou detectar retenção do predecessor, abrir incidente e manter o agregado bloqueado. Tempo decorrido sozinho não comprova perda permanente. Verificar estado transacional, Outbox, confirmação de entrega e efeitos do consumidor. Distinguir predecessor ausente de predecessor retido ou indisponível por política de retenção. |
| Reconciliação e retomada | Recuperar e validar o evento original a partir de fonte autoritativa ou escalar se a origem não puder ser comprovada. Qualquer correção excepcional exige decisão humana e trilha de auditoria. Preservar identidade, sequência e conteúdo histórico. A retomada exige confirmar a cadeia e os efeitos já aplicados e verificar replay idempotente. Evitar salto de versão, reordenação automática e reenvio de resultado incerto sem reconciliação. |

A quarentena proposta é um bloqueio auditável por agregado. O registro deve identificar escopo, versão esperada e observada, eventos envolvidos, primeira detecção UTC, motivo, correlação, evidência e decisão de resolução. Sua persistência deve sobreviver a reinícios e concorrência. A forma de armazenamento, retenção e alertas depende de revisão com DOC-05. Se a gravação de estado e Outbox for revertida, a evidência do conflito precisa de um caminho durável que sobreviva ao rollback.

## Testes e evidências existentes

| Testes de integração no checkout oficial | Evidência histórica e limite |
|---|---|
| `test_out_of_order_arrival_waits_for_missing_version` e `test_dispatcher_orders_pending_versions_and_skips_locked_rows` | Espera pela versão anterior, progresso de outro agregado e ordem após chegada tardia. [Resiliência](../evidence/I00-13-resiliencia.md) |
| `test_dispatcher_retries_then_retains_failed_event` e `test_dispatcher_retry_recovers_after_publisher_unavailability` | Retry, retenção após falha persistente e recuperação de indisponibilidade transitória. [Dispatcher](../evidence/I00-06-dispatcher.md) · [Resiliência](../evidence/I00-13-resiliencia.md) |
| `test_duplicate_event_rolls_back_new_state`, `test_duplicate_deliveries_apply_one_effect_across_restarts` e `test_consumer_rolls_back_effect_and_deduplication` | Rollback ao repetir event_id, efeito único após replay e rollback conjunto do consumidor. O cenário de IDs distintos na mesma versão requer teste próprio. [Outbox](../evidence/I00-05-outbox.md) · [Consumidor](../evidence/I00-07-consumidor.md) |

[Suíte de integração PostgreSQL](../../tests/integration/test_postgres_migrations.py)

## Validação pendente

- Aprovar cardinalidade de eventos por versão, igualdade de conteúdo, identidade do agregado e estratégia para registros existentes. Testar escritores e dispatchers concorrentes, IDs iguais com conteúdo divergente, IDs distintos na mesma versão e escopos separados por ambiente ou conta.
- Aprovar relógio, limiar de alerta, retenção, responsáveis e fonte autoritativa. Testar predecessor que nunca chega, predecessor retido e evento anterior indisponível por retenção. Demonstrar bloqueio durável sem consumir tentativas indevidas e avanço de outros agregados.
- Aprovar o procedimento de reparo e liberação. Testar chegada tardia após quarentena, restart durante reparo, conflito após publicação e replay sem efeito financeiro ou projeção duplicados. Vincular resultados ao candidato e aos critérios AC07/08.

Os testes foram conferidos pelo nome com PowerShell e `rg`. Os resultados citados são históricos. **DOC-04 permanece aberto para aprovação da política e validação em PostgreSQL.**

A aprovação de 16/11/2026 abrange a proposta documental. Os parâmetros delegados a revisão após os ensaios e o aceite técnico do critério permanecem pendentes. LIVE permanece indisponível.
