# Parecer técnico e cobertura — TS-ST-001 a TS-ST-004

Data 17/11/2026. Referência de código 0172728bd36c23247987a28c0fdccd32488e06f3.
Estado IN_REVIEW para revisão dos responsáveis e aceite humano. As quatro decisões de escopo foram aprovadas pelo usuário após a execução do candidato.

## Evidências utilizadas

[Execução dos 20 critérios](RESULTADOS.md) e [inventários do candidato](INVENTARIOS-ESCOPO.md). A rodada registrada passou em 153 testes com PostgreSQL local, 39 testes em extração limpa e 12 casos adicionais de compatibilidade. Instalação, build, Ruff, formatação e mypy aprovados no recorte Windows. A conclusão desta revisão usa essas evidências e leitura estática do SHA; resultados de execução mantêm sua data e seu recorte.

## TS-ST-001 — revisão de fronteiras

O mapeamento físico src/trade_system, apps/api e infrastructure foi aprovado pelo usuário. O grafo das importações explícitas entre módulos em src/trade_system foi conferido por AST e terminou sem ciclos.

As nove ocorrências de importação cruzada se agrupam em execution→control/risk, risk→control, market_state→features/market_data e market_data→risk. As duas primeiras sustentam a sequência de autorização e avaliação da simulação. Market State usa cálculo de features e constantes temporais de mercado. Market Data importa FundingObservation e LiquidationMark de risk.futures como tipos de transferência; essa dependência de tipos merece acompanhamento quando evoluir a separação dos domínios. O recorte I00 aqui aprovado verifica estrutura e imports. A conformidade operacional integral dos módulos de incrementos posteriores exige sua própria revisão.

ST001-AC01 possui suporte técnico no recorte físico aprovado, com a observação de dependência de tipos registrada. ST001-AC02 passou na instalação e build limpos. ST001-AC03 continua parcial até CI remoto no SHA e evidência do bloqueio por falha obrigatória. ST001-AC04 tem rastreabilidade consolidada neste parecer, aguardando responsáveis e parecer QA.

## TS-ST-002 — relatório de cobertura P90/P61

| Artefato | Cobertura demonstrada | Encaminhamento |
|---|---|---|
| CommandEnvelope 1.0.0 | Exemplo, campos obrigatórios, tipos, ambientes, UTC, versão desconhecida e campos adicionais | Aceite técnico no recorte aprovado |
| EventEnvelope 1.0.0 | Mesma cobertura e aggregate_version mínimo | Aceite técnico no recorte aprovado |
| Matriz de compatibilidade | Seis casos por envelope contra consumidor v1; 12 casos aprovados | Referência para evolução posterior de versões |
| Payloads específicos de domínio | Envelope exige objeto; schemas de conteúdo próprios aguardam definição por domínio | Cobertura remanescente de P61/P90 |
| Modelos auxiliares Pydantic | Inventariados no código e vinculados aos respectivos recortes de API e aplicação | Manter revisão na Feature/história correspondente |
| Schema registry e catálogo global de contratos | Cobertura remanescente identificada | Designar responsável e planejamento quando tratar P61 integralmente |

ST002-AC01/02/04 têm demonstração no recorte v1. ST002-AC03 aprovado documentalmente. ST002-AC05 recebe o relatório de cobertura acima para o recorte aprovado. A atribuição nominal do trabalho remanescente continua pendente.

## TS-ST-003 — ownership e transação do produtor sintético

Nos ensaios, a fixture do produtor escreve outbox_test_state e chama append_event passando a mesma conexão SQLAlchemy dentro da transação. append_event exige transação ativa. Estado e Outbox compartilham commit/rollback. Em conflito a função reverte a transação do produtor e grava incidente/quarentena por conexão independente. As evidências de commit, rollback, concorrência e event_id divergente estão na suíte PostgreSQL aprovada.

As 41 chamadas explícitas de append_event estão em testes. O produtor sintético assume ownership do estado de teste e envia a mensagem para a infraestrutura de eventos. A identidade de versão é controlada no escopo ambiente, conta, tipo e ID do agregado. A aplicação da regra de um evento por versão foi aceita pelo usuário para esse recorte sintético.

A reconstrução dos dados sintéticos usa fixtures e procedimentos do ensaio. Para eventos de produtores operacionais, a validação integral anterior a append_event e a fonte autoritativa de recuperação continuam obrigações de integração.

ST003-AC01–04 possuem evidência de execução no recorte registrado. ST003-AC05 tem ownership técnico e fronteira transacional descritos neste parecer, sujeitos à revisão de QA. A verificação de legado só se aplica quando uma base persistente específica for selecionada para integração.

## TS-ST-004 — publisher e consumidor

O dispatcher chama LocalPublisher, que confirma uma gravação durável em event_delivery usando transação própria. Uma interrupção entre entrega e confirmação de publicação pode gerar reentrega; os ensaios verificam o efeito idempotente. O consumidor aplica apply_diagnostic_event, registra processed_event e consumed_at na mesma transação. A chave de deduplicação é event_id.

O usuário aprovou um consumidor lógico diagnóstico e o publisher local no recorte de aceite. A comparação com múltiplos consumidores independentes fica registrada como requisito para futura evolução. ST004-AC02 possui demonstração de efeito único no recorte aprovado; revisar identidade de deduplicação ao introduzir outro consumidor lógico.

ST004-AC01/03/04 têm evidência local. ST004-AC05 tem mecanismos de autorização e retomada ensaiados, mas depende de designação de operadores para aplicação operacional. ST004-AC06 tem cálculos e transições ensaiados; frequência e alertas estão na proposta para aprovação.

## Síntese para aceite técnico

| Grupo | Resultado desta revisão | Pendência de aceite |
|---|---|---|
| ST001-AC01 | Revisão física concluída no recorte aprovado | Parecer de QA e decisão sobre a observação das dependências de tipos |
| ST001-AC03 | Etapas locais passaram | CI remoto e bloqueio por falha |
| ST001-AC04 | Rastreabilidade consolidada | Designação e parecer técnico/QA |
| ST002-AC05 | Cobertura dos envelopes e remanescente documentados | Revisão de QA e atribuição do remanescente |
| ST003-AC05 | Ownership sintético e atomicidade descritos | Revisão de QA; legado quando houver base alvo |
| ST004-AC02 | Consumidor único aprovado e ensaiado | Revisão de QA |
| ST004-AC05 | Mecanismos locais ensaiados | Operadores e autoridades nominais |
| ST004-AC06 | Métricas locais verificadas | Aprovação e configuração de monitoramento |

[Proposta de monitoramento](MONITORAMENTO-PROPOSTA.md). As fichas continuam com aprovação documental; a decisão de aceite técnico da entrega é posterior aos pareceres e pendências acima.
