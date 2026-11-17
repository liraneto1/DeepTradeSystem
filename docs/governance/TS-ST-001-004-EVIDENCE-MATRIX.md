# Matriz de evidências — TS-ST-001 a TS-ST-004

Data de elaboração 17/11/2026. Estado APPROVED. Responsabilidades funcionais, vínculos, critérios e referências iniciais de compatibilidade e parâmetros aprovados pelo usuário nesta conversa.

A matriz confronta os 20 critérios aprovados com evidências históricas e inspeção documental. As verificações de execução estão pendentes de confirmação no candidato. A aprovação documental de ST002-AC03 está registrada; sua aplicação técnica será verificada no candidato.

## Referências de configuração

Python 3.12, uv 0.9.26 e Hatchling 1.28.0 conforme arquivos do checkout. Verificar instalação bloqueada, qualidade e build segundo o [workflow CI](../../.github/workflows/ci.yml) e o [pyproject](../../pyproject.toml).

Política de compatibilidade aprovada em [TS-ST-002](../backlog/TS-ST-002.md). Parâmetros iniciais aprovados em [TS-ST-004](../backlog/TS-ST-004.md).

## Cobertura por critério

| Critério | Evidência existente | Cobertura observada | Verificação faltante | Estado |
|---|---|---|---|---|
| ST001-AC01 | [I00-bootstrap.md](../evidence/I00-bootstrap.md) | Imports e estrutura no bootstrap histórico. | Confrontar árvore e fronteiras com I00-FEAT-001 no candidato; registrar desvios. | Pendente de verificação no candidato |
| ST001-AC02 | [I00-bootstrap.md](../evidence/I00-bootstrap.md) · [AC02-d561026-digest-triage.md](../evidence/AC02-d561026-digest-triage.md) | Instalação/build históricos e triagem parcial de dependências. | Reproduzir checkout limpo, conferir lockfile, toolchain e artefatos resolvidos no ambiente alvo. | Pendente de verificação no candidato |
| ST001-AC03 | [I00-bootstrap.md](../evidence/I00-bootstrap.md) | Registro de CI histórico e workflow de qualidade disponível. | Relacionar execução completa ao candidato; confirmar bloqueio por falha de build ou teste. | Pendente de verificação no candidato |
| ST001-AC04 | [I00-12-rastreabilidade.md](../evidence/I00-12-rastreabilidade.md) | Registro mestre liga pacotes e evidências históricas. | Consolidar I00-01/02/11 e pareceres técnico e QA para o candidato. | Pendente de verificação no candidato |
| ST002-AC01 | [I00-03-contratos.md](../evidence/I00-03-contratos.md) | Exemplos sintéticos e schemas v1; testes de contrato disponíveis. | Executar exemplos de ambos os envelopes no candidato e guardar resultados por versão. | Pendente de verificação no candidato |
| ST002-AC02 | [I00-03-contratos.md](../evidence/I00-03-contratos.md) | Casos de campos ausentes, tipos, UTC, ambientes, versão e campo extra no arquivo de testes. | Reexecutar os casos e mapear os resultados aos requisitos do contrato. | Pendente de verificação no candidato |
| ST002-AC03 | [Política registrada](../backlog/TS-ST-002.md) | Política inicial aprovada nesta conversa e registrada em TS-ST-002 nesta atualização. | Designar revisão técnica e controlar futuras alterações da política. | APPROVED documental; verificação técnica pendente |
| ST002-AC04 | [I00-03-contratos.md](../evidence/I00-03-contratos.md) | Validação v1 e rejeição de versão desconhecida documentadas. | Completar matriz produtor/consumidor para campos adicionais, remoções, tipos e valores; registrar resultados. | Pendente de verificação no candidato |
| ST002-AC05 | [I00-03-contratos.md](../evidence/I00-03-contratos.md) | DOC-03 delimita envelopes e lacunas de contratos de domínio. | Produzir lista de contratos cobertos e pendentes de P90/P61, com responsáveis. | Pendente de verificação no candidato |
| ST003-AC01 | [I00-04-postgresql.md](../evidence/I00-04-postgresql.md) | Migrações iniciais têm ensaio histórico. | Confirmar cadeia completa do candidato, migrações até 0022 conforme aplicabilidade e reversão suportada. | Pendente de verificação no candidato |
| ST003-AC02 | [I00-05-outbox.md](../evidence/I00-05-outbox.md) | Commit conjunto de estado e Outbox documentado. | Reproduzir no candidato e conservar consultas antes e depois. | Pendente de verificação no candidato |
| ST003-AC03 | [I00-05-outbox.md](../evidence/I00-05-outbox.md) | Rollback conjunto e duplicidade têm referência histórica. | Conferir falhas entre gravações e antes do commit, com estado observado no candidato. | Pendente de verificação no candidato |
| ST003-AC04 | [AC07-conflito-concorrente-outbox.md](../evidence/AC07-conflito-concorrente-outbox.md) · [AC07-event-id-divergente.md](../evidence/AC07-event-id-divergente.md) | Conflito concorrente, replay equivalente e event_id divergente têm ensaios documentados. | Conferir hashes e migração 0022 no candidato; reproduzir cenários e validar incidentes duráveis. | Pendente de verificação no candidato |
| ST003-AC05 | [AC07-consolidacao-aceite-tecnico.md](../evidence/AC07-consolidacao-aceite-tecnico.md) · [AC07-event-id-divergente.md](../evidence/AC07-event-id-divergente.md) | Constraints e concorrência têm registros; confirmação de produtores permanece aberta. | Confirmar um evento por versão por produtor, ownership e fonte de recuperação; verificar colisões legadas. | Pendente de verificação no candidato |
| ST004-AC01 | [I00-06-dispatcher.md](../evidence/I00-06-dispatcher.md) · [I00-13-resiliencia.md](../evidence/I00-13-resiliencia.md) | Publicação, retry e reinício documentados no recorte local. | Conferir progresso persistido e reentrega no candidato e no publisher efetivamente usado. | Pendente de verificação no candidato |
| ST004-AC02 | [I00-07-consumidor.md](../evidence/I00-07-consumidor.md) · [I00-13-resiliencia.md](../evidence/I00-13-resiliencia.md) | Deduplicação e rollback do efeito no consumidor local têm ensaios históricos. | Confirmar escopo por consumidor lógico; verificar concorrência, reinício e efeito único no candidato. | Pendente de verificação no candidato |
| ST004-AC03 | [AC07-parametros-operacionais.md](../evidence/AC07-parametros-operacionais.md) · [I00-06-dispatcher.md](../evidence/I00-06-dispatcher.md) | Cinco tentativas e backoff no código; retenção e escalonamento em ensaio histórico. | Conferir parâmetros aprovados, retenção elegível, recuperação transitória e falha terminal no candidato. | Pendente de verificação no candidato |
| ST004-AC04 | [AC07-quarentena-retomada.md](../evidence/AC07-quarentena-retomada.md) · [AC07-escalonamento-predecessor.md](../evidence/AC07-escalonamento-predecessor.md) | Espera sem tentativas, agregados independentes e escalonamento têm registros. | Reproduzir ausência, chegada tardia, predecessor retido e reinício com cadeia identificada. | Pendente de verificação no candidato |
| ST004-AC05 | [AC07-autorizacao-outbox.md](../evidence/AC07-autorizacao-outbox.md) · [AC07-dispatcher-login-restrito.md](../evidence/AC07-dispatcher-login-restrito.md) · [AC07-event-id-divergente.md](../evidence/AC07-event-id-divergente.md) | Autorização, login restrito, reparo e incidente durável documentados. | Designar operadores e validar grants no alvo, autoridade de reparo/retomada e origem autoritativa. | Pendente de verificação no candidato |
| ST004-AC06 | [AC09-coletor-outbox.md](../evidence/AC09-coletor-outbox.md) | Ensaio de snapshot, transições, indisponibilidade e segregação documentado. | Conferir código pelo manifesto; reproduzir métricas no candidato e definir frequência e limiares. | Pendente de verificação no candidato |

## Candidato e integridade

O código, os contratos, os testes, pyproject.toml e uv.lock coincidem com HEAD local 184e8b30a8dc9d812bce092e893f70a8931c4570, que já contém as mudanças de Outbox e a migração 0022. O próximo candidato proposto acrescenta a documentação revisada a essa base.

A conferência de 17/11/2026 encontrou 8 de 8 hashes coincidentes no manifesto AC07-event-id-sha256.txt. No manifesto antigo AC09-outbox-metrics-sha256.txt, 5 coincidem e 3 divergem: infrastructure/events/dispatcher.py, infrastructure/events/outbox.py e tests/integration/test_postgres_migrations.py. A cobertura de métricas exige reconfirmação no candidato selecionado. As datas e bases históricas dos ensaios permanecem registradas nos respectivos documentos.

[Manifesto de event_id](../evidence/AC07-event-id-sha256.txt) · [Manifesto de métricas](../evidence/AC09-outbox-metrics-sha256.txt)

## Responsabilidade pelas próximas verificações

Engineering Architecture responde funcionalmente por TS-ST-001/002. Data & Event Architecture responde por TS-ST-003/004. Responsáveis técnicos, QA e operadores individuais aguardam designação. Cada execução deve registrar commit, ambiente, configuração, resultado esperado e observado e referência aos logs sanitizados.


## Aprovação da matriz

17/11/2026 · Matriz dos 20 critérios aprovada pelo usuário nesta conversa. Verificações por candidato permanecem com os estados registrados nas linhas.