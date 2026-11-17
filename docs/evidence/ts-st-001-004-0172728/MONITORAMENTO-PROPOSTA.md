# Proposta de monitoramento — TS-ST-004

Data 17/11/2026. Estado APPROVED pelo usuário nesta conversa em 17/11/2026. Aplicável ao publisher PostgreSQL e consumidor diagnóstico em TRAINING/PAPER. Os parâmetros desta proposta ainda dependem de implementação/configuração do agendamento e dos alertas.

## Referências já aprovadas

Cinco tentativas totais; backoff de 1, 2, 4 e 8 segundos; pausa sem elegível de 1 segundo; escalonamento de lacuna em 3.600 segundos; retenção mínima de 30 dias com remoção manual condicionada; janela de métricas de 300 segundos.

## Parâmetros propostos

| Parâmetro | Proposta | Ação esperada |
|---|---|---|
| Frequência de coleta | Uma coleta a cada 30 segundos | Preservar instante UTC, ambiente e resultado da coleta |
| Janela de métricas | 300 segundos | Usar janela aprovada; considerar sobreposição ao apresentar contagens por intervalo |
| Coleta indisponível | Duas falhas consecutivas ou 60 segundos sem amostra bem-sucedida | Abrir alerta de indisponibilidade; manter última amostra identificada como desatualizada |
| Falha terminal ou quarentena | Uma ocorrência confirmada, detectada na próxima coleta ou evento de log | Abrir incidente por agregado; encaminhar para revisão |
| Espera por predecessor | Acompanhamento informativo até o limiar de 3.600 segundos | Escalar conforme DOC-04; predecessor comprovadamente retido ou falho segue o escalonamento imediato existente |
| Evento elegível mais antigo | Aviso após 300 segundos em duas amostras consecutivas; crítico após 900 segundos em duas amostras | Investigar dispatcher, permissões e dependências; valores iniciais sujeitos ao ensaio de carga |
| Volume absoluto de backlog | Medir referência antes de fixar limite | Registrar volume e taxa de entrada/publicação durante ensaio representativo |
| Encerramento de alerta de coleta ou atraso | Duas amostras consecutivas dentro da condição normal | Registrar recuperação; incidentes de quarentena dependem de reconciliação e autorização |
| Identidade dos alertas | Ambiente, condição e agregado no registro de incidente | Deduplicar notificações do mesmo incidente; métricas mantêm dimensões de cardinalidade limitada |

A idade do elegível exclui espera por predecessor, retry futuro e falha retida, conforme categorias DOC-05. O atraso dos eventos publicados é acompanhado por contagem, mínimo, p50, p95 e máximo. Limiares quantitativos para essa distribuição exigem ensaio de referência.

## Verificações de implantação pendentes

- Confirmar agenda de 30 segundos e falhas de execução do coletor.
- Demonstrar as transições dos alertas com tempo controlado.
- Confirmar exclusão das categorias de espera e retry do alerta de elegíveis.
- Designar destinatários, canal e responsável por atendimento.
- Medir carga representativa e revisar os limiares de 300 e 900 segundos.
- Registrar autorização e execução de retenção e retomada por operadores identificados.

A proposta especifica monitoramento. Decisões de reparo e retomada mantêm a autoridade humana definida em DOC-04.

## Registro da aprovação

17/11/2026 · Usuário aprovou os parâmetros propostos. Agendamento, alertas e ensaio de implantação permanecem pendentes conforme a seção de verificações.