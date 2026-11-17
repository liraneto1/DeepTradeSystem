# TS-ST-004 — Agendamento local e transições de alerta

17/11/2026. Implementação posterior ao candidato 0172728bd36c23247987a28c0fdccd32488e06f3. Implementação e resultados APPROVED pelo usuário nesta conversa em 17/11/2026. Escopo publisher PostgreSQL local e consumidor diagnóstico em TRAINING/PAPER.

## Entrega

- Novo módulo apps/event_dispatcher/monitor.py com agenda de 30 s e janela de 300 s.
- Estado e histórico transacionais em SQLite, separados por ambiente, persistentes após reinício.
- Alertas de coleta, idade do elegível e incidentes de quarentena.
- Coleta opcional de incidentes no mesmo snapshot PostgreSQL; chamadas anteriores preservam o formato de resposta.
- Diretório .runtime ignorado pelo Git para arquivos operacionais locais.
- Procedimento em docs/runbooks/monitor-outbox.md.

## Verificações executadas

Ruff aprovado, formatação aprovada e mypy sem problemas em 98 arquivos. Suíte completa passou com 164 testes em 95,22 s. PostgreSQL 17 descartável na porta 58474, loopback, PAPER e LIVE_ENABLED=false; instância encerrada ao final. O código novo foi verificado no checkout com alterações, sobre a base 0172728; seu próprio commit ainda deverá ser definido.

## Transições cobertas pelos testes

| Cenário | Resultado |
|---|---|
| Duas falhas consecutivas | Abre alerta de coleta |
| Duas amostras válidas após falha | Recupera alerta de coleta |
| 60 s sem coleta válida | Detecta indisponibilidade ao retomar observações |
| Duas amostras acima de 300 s | Aviso de idade do elegível |
| Duas amostras acima de 900 s | Escalonamento crítico |
| Duas amostras normais | Recuperação de idade |
| Falha entre confirmações de idade | Reinicia confirmação consecutiva |
| Espera por predecessor e retry futuro | Excluídos do alerta de idade elegível |
| Incidente repetido e reinício | Uma transição de abertura por ID, com escopo persistido |
| Retomada com estado persistido | Preserva confirmação e histórico |
| Observação fora de ordem | Rejeita e reverte alteração do estado |
| Ambiente divergente | Rejeita observação |
| Agenda com coleta de 2 s | Espera complementar de 28 s, janela de 300 s |
| Quarentena no PostgreSQL | Incidentes coletados no snapshot das métricas |

## Continuidade e operação

O modo contínuo agenda enquanto o processo está em execução. Inicialização como serviço e supervisão externa da interrupção completa do processo aguardam a definição da conta de execução e do ambiente definitivo. O alerta de ausência é detectado no próximo ciclo do monitor. O diário SQLite e a saída JSON são o destino local; canal externo e destinatários aguardam designação. Incidentes mantêm trilha para reconciliação e decisão humana.

[Procedimento de execução](../../runbooks/monitor-outbox.md)