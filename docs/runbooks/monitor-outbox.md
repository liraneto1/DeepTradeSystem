# Monitor local de Outbox — TS-ST-004

O módulo apps.event_dispatcher.monitor agenda uma coleta a cada 30 segundos enquanto seu processo está ativo. A janela de métricas é 300 segundos. A agenda desconta o tempo gasto na coleta e persiste o estado de alerta e o histórico em SQLite. Cada ambiente tem estado separado.

## Execução

No ambiente local já configurado com POSTGRES_PASSWORD, POSTGRES_PORT, TRADE_SYSTEM_ENVIRONMENT=PAPER ou TRAINING e LIVE_ENABLED=false:

    uv run --no-sync python -m apps.event_dispatcher.monitor --state-file .runtime/outbox-monitor.sqlite

Para uma coleta:

    uv run --no-sync python -m apps.event_dispatcher.monitor --state-file .runtime/outbox-monitor.sqlite --once

Usar um único processo agendador por arquivo/ambiente. SQLite serializa atualizações e observações fora de ordem são rejeitadas. O arquivo de estado deve ficar em diretório local controlado pelo operador. Interromper com Ctrl+C encerra o engine; o próximo início reutiliza as confirmações e incidentes registrados.

## Transições

- Duas falhas consecutivas ou 60 segundos desde a última coleta válida abrem indisponibilidade.
- Duas amostras válidas consecutivas encerram indisponibilidade.
- Idade de elegível acima de 300 segundos em duas amostras gera aviso; acima de 900 segundos em duas amostras gera crítico.
- Duas amostras com idade até 300 segundos, ou categoria elegível vazia, encerram o alerta de idade.
- Falha de coleta interrompe a confirmação consecutiva de idade e recuperação.
- Quarentena aberta gera incidente na primeira amostra que a observa, incluindo motivo e escopo do agregado. O mesmo ID de incidente é registrado uma única vez, inclusive após reinício. A saída da quarentena preserva o histórico do incidente; a resolução humana segue DOC-04.
- Falha terminal do dispatcher usa a quarentena existente. A coleta observa esses registros no mesmo snapshot das métricas.
- Espera por predecessor, retry futuro e falha retida ficam fora do cálculo de idade da categoria elegível.

A tabela monitor_transition guarda observação UTC, ambiente e evento de transição. A saída JSON do processo serve ao acompanhamento local. Destinatários e canal externo dependem de designação posterior.

## Continuidade

A detecção de ausência de amostra acontece quando o monitor executa novamente. Detectar a interrupção completa do processo durante sua ausência depende de supervisão externa. A configuração de inicialização do serviço e desse supervisor deve ser feita no ambiente definitivo, após definir operador e conta de execução.

As consultas PostgreSQL são de leitura. O estado do monitor é gravado somente no arquivo SQLite indicado. Eventos de teste e incidentes operacionais mantêm o ambiente no registro. A coleta opcional de incidentes preserva a resposta original do coletor existente quando desabilitada.