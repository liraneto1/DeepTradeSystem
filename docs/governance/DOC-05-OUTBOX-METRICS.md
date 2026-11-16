# DOC-05 Métricas de backlog e atraso da Outbox

**16/11/2026 · APPROVED · proposta aprovada pelo usuário nesta conversa.** T06 prevê métricas de atraso, tentativas, falhas e backlog. Este documento propõe as definições para I00-AC09, vinculadas a I00-06, I00-10, I00-13, P51, P75 e TS-ADR-096. As evidências de diagnóstico, logs e correlação sustentam cobertura parcial de AC09. G0 segue aberto. LIVE permanece indisponível.

[Engineering Foundation, T06](<../referencias/originais/TS-ENG-I00-V1.0 - Engineering Foundation.txt>) · [Revisão RC1](../evidence/revisao-g0-i00-rc1.md) · [Matriz I00](DOC-03-I00-TRACEABILITY.md)

## Decisões aprovadas e parâmetros a definir

1. **O que contar.** Aprovar backlog como total de eventos ainda sem publicação e a divisão exclusiva em retidos, bloqueados por ordenação, aguardando disponibilidade e elegíveis. A precedência das categorias está na tabela abaixo.
2. **O que medir em segundos.** Aprovar idade desde a entrada na Outbox e atraso até a publicação, incluindo espera e retry. A duração desde a detecção de um bloqueio depende do marco de DOC-04. Tentativas, retries e falhas terminais são contagens por intervalo.
3. **Como apresentar e alertar.** Aprovar amostragem coerente em UTC, segregação por ambiente, distinção entre fila vazia e coleta indisponível e dimensões de cardinalidade limitada. Designar quem aprova janelas, frequência e limiares após a medição de referência. Os valores permanecem em aberto.

## Evidência de Engenharia para fechar AC09

| Cenário | Critério verificável |
|---|---|
| Amostra conhecida | Conferir total, categorias e idade por ambiente contra o mesmo snapshot PostgreSQL. Cobrir fila vazia, elegibilidade, retry futuro, bloqueio por versão e falha retida. A soma das categorias coincide com o total. |
| Transição e atraso | Demonstrar que a publicação reduz o backlog e que o atraso medido inclui espera e retry. A idade do pendente não reinicia ao reagendar. Conferir tentativas, retries e falhas terminais sem dupla contagem. |
| Falha e reinício da coleta | Diferenciar indisponibilidade de zero, preservar segregação e verificar que dimensões e logs não expõem payloads ou segredos. |

Anexar ao candidato comando, configuração, dados de teste, valores esperados e observados e resultado de QA. Usar PostgreSQL isolado, TRAINING ou PAPER e LIVE_ENABLED=false. Os registros históricos abaixo demonstram o fluxo e a correlação.

## Definições propostas

A fonte é a tabela transacional da Outbox no PostgreSQL. Cada amostra usa um único instante UTC do banco e considera somente linhas visíveis no snapshot de leitura. O escopo mínimo é por ambiente TRAINING ou PAPER. IDs de evento, agregado, conta e correlação ficam nos registros de diagnóstico sanitizados conforme a política aplicável. As dimensões de métrica devem ter cardinalidade limitada.

| Métrica | Unidade e regra |
|---|---|
| Backlog total | Eventos com `published_at` ausente. Inclui espera por predecessor, eventos elegíveis, espera por disponibilidade e falhas retidas. Fila vazia vale zero. |
| Backlog por condição | Contagem de eventos não publicados em grupos mutuamente exclusivos. Classificar primeiro os retidos (`failed_at` preenchido), depois os bloqueados pela regra de ordenação do dispatcher, depois os com `available_at` futuro e, por fim, os elegíveis. Um evento elegível pode estar bloqueado por outro worker naquele instante. A soma dos grupos deve coincidir com o total no mesmo snapshot. |
| Idade do backlog | Segundos entre `enqueued_at` do evento não publicado mais antigo e o instante da amostra. Publicar a idade do mais antigo por ambiente e, se necessário, por condição. Indicar ausência de observação para grupo vazio. |
| Atraso de publicação | Distribuição em segundos de `published_at - enqueued_at` para eventos publicados no intervalo medido, com contagem de observações. Inclui espera por versão e retry. O marco final é o registro da publicação no dispatcher. A conclusão do consumo requer outra medição. |
| Tentativas e falhas | Contagem de tentativas registradas, retries agendados e transições para falha terminal no intervalo medido. Vincular ao registro persistido ou à telemetria de transição com regra explícita de deduplicação. O tamanho do backlog retido é uma medida de estoque. |

`available_at` representa a próxima disponibilidade e pode avançar após retry. A idade total usa `enqueued_at` para preservar o tempo já esperado. As métricas de bloqueio devem usar a mesma regra de predecessor do dispatcher. Medir a duração **desde a detecção do bloqueio** exige um marco próprio, a validar com DOC-04. Definir também como sinalizar coleta indisponível para distingui-la de fila vazia. [Outbox](../../infrastructure/events/outbox.py) · [Dispatcher](../../infrastructure/events/dispatcher.py) · [DOC-04](DOC-04-OUTBOX-ORDERING.md)

## Evidências disponíveis

| Evidência ou teste localizado | Contribuição para AC09 |
|---|---|
| `test_correlation_traces_api_dispatcher_and_consumer` | Logs e correlação em três processos, com payload fora dos logs. [Telemetria I00](../evidence/I00-10-telemetria.md) |
| `test_out_of_order_arrival_waits_for_missing_version` | Cenário para verificar backlog bloqueado. A versão posterior espera sem consumir tentativas e outro agregado avança. [Resiliência I00](../evidence/I00-13-resiliencia.md) |
| `test_dispatcher_retry_recovers_after_publisher_unavailability` e `test_dispatcher_retries_then_retains_failed_event` | Cenários para verificar espera por retry, redução após publicação e estoque retido após falha terminal. [Dispatcher I00](../evidence/I00-06-dispatcher.md) · [Resiliência I00](../evidence/I00-13-resiliencia.md) |

[Suíte PostgreSQL](../../tests/integration/test_postgres_migrations.py)

## Validação pendente para AC09

- Aprovar regras de amostragem, agrupamento, janela de atraso, tratamento de timestamps inconsistentes, responsáveis e limiares de alerta. Acordar a fonte das contagens por intervalo e a coordenação com DOC-04.
- Em PostgreSQL isolado, preparar fila vazia, elegível, aguardando retry, bloqueada por versão e retida. Comparar métricas com registros esperados no mesmo snapshot. Demonstrar que o backlog cai após publicação, a idade não reinicia com retry, a latência inclui a espera e os ambientes são segregados.
- Verificar reinício e indisponibilidade da coleta, ausência de duplicação nas contagens por intervalo, cardinalidade das dimensões e ausência de payloads e segredos na telemetria. Registrar comando, configuração, valores esperados e observados e identidade do candidato no Evidence Bundle.

Os testes citados foram localizados pelo nome. Os resultados vinculados são históricos e cobrem o comportamento do fluxo. **DOC-05 permanece aberto e AC09 continua parcial até que as métricas sejam demonstradas no candidato.**

A aprovação de 16/11/2026 abrange a proposta documental. Os parâmetros delegados a revisão após os ensaios e o aceite técnico do critério permanecem pendentes. LIVE permanece indisponível.
