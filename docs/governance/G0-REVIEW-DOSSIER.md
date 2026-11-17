# Dossiê de revisão de G0

**12/11/2026 · IN_REVIEW · Decisão humana pendente.** G0 verifica a prontidão de engenharia do Trade System V1. O Blueprint trata I00–I02 como contribuições parciais e vincula I03 e I04 ao gate. G49 mantém o aceite por incremento e a decisão de gate independentes. **LIVE permanece indisponível.**

[Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) · [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) · [DOC-03 consolidado](DOC-03-CONSOLIDATION.md)

## Validações pendentes de Engenharia para G0

Em 16/11/2026, o usuário aprovou o TS-DOC-STD-V1.0, os sete templates e a classificação dos bloqueios de I00. **G0 continua IN_REVIEW e LIVE permanece indisponível.** [Aprovação](APPROVAL-REGISTER.md) · [Bloqueios](GAP-REGISTER.md)

| Item | Validação e evidência a entregar |
|---|---|
| **AC02 · Dependências** | No candidato `d561026`, concluir a triagem da imagem PostgreSQL por digest e identificar no runner Linux os componentes nativos instalados e carregados, suas versões efetivas e avisos aplicáveis. Registrar a resolução do build isolado, incluindo CPython, uv, Hatchling e transitivas, com logs e hashes de wheel e sdist. Se o digest mudar, auditar a nova imagem e repetir a integração. QA confere a correspondência entre commit, lockfile, plataforma, digest, CI e artefatos. Segurança decide correções ou exceções com responsável e validade. [Critérios aprovados](AC02-ENGINEERING-ACCEPTANCE.md) · [Retorno parcial](../evidence/AC02-d561026-retorno-engenharia.md) |
| **AC07 · Ordenação da Outbox** | Confirmar com os donos dos produtores a regra de um evento por versão e a fonte autoritativa do envelope. Com Administração do Banco e QA, executar a pré-checagem somente leitura em snapshot autorizado anterior à migração 0016 e registrar origem, contagens e eventual reconciliação. Engenharia e QA revisam controles operacionais, parâmetros e a aplicabilidade dos 153 testes PostgreSQL do candidato `184e8b3` ao candidato de G0. [Política aprovada](DOC-04-OUTBOX-ORDERING.md) · [Pré-checagem](../evidence/AC07-produtores-e-colisoes-legadas.md) |
| **AC09 · Métricas da Outbox** | Vincular ou repetir no candidato de G0 os testes PostgreSQL do coletor. Entregar valores esperados e observados para backlog e atraso em janela explícita, contagens deduplicadas, fila vazia versus indisponibilidade e duração desde a detecção de bloqueio. Submeter frequência, janela, limiares, retenção, tratamento de timestamps inconsistentes e responsáveis à decisão humana. [Definições aprovadas](DOC-05-OUTBOX-METRICS.md) · [Evidência do coletor](../evidence/AC09-coletor-outbox.md) |
| **Candidato e decisão de G0** | Engenharia e QA identificam o candidato submetido, cruzam evidências de I00–I04 com versões e ambientes, identificam reexecuções e entregam parecer por bloqueio. O aceite de I00-14 e AC12 permanece no escopo original do bundle RC1. A decisão humana de G0 deve ser registrada com data, escopo, candidato, evidências e condições. [Aceite RC1](DOC-07-RC1-ACCEPTANCE.md) |

Para cada execução, anexar commit, ambiente, versões, comando ou link de CI, resultados e limitações. Nas reexecuções de integração de I00, usar ambiente de teste isolado, PostgreSQL descartável, credenciais de teste e `LIVE_ENABLED=false`.

## Evidências por incremento

| Incremento | Evidência e alcance do aceite | O que ainda precisa ser demonstrado para G0 |
|---|---|---|
| I00 · Fundação · TS-ST-001–004 | RC1 no commit `8d1467dd4087bcb6bb37fd4cc880de6d42b661e6`. O CI histórico registra 69 testes gerais e 16 de integração PostgreSQL 17 aprovados. O aceite humano de 11/11 cobre I00-14 e o bundle. Os oito hashes conferiram em 12/11. [DOC-07 e AC12](DOC-07-RC1-ACCEPTANCE.md) · [Matriz I00](DOC-03-I00-TRACEABILITY.md) | Fechar ou registrar tratamento formal de AC02, AC07 e AC09 no candidato submetido à revisão. |
| I01 · Dados de mercado · TS-ST-005/006 | A consolidação registra carga de 4.032 candles, reimportação, restauração e retomada de ingestão. A ingestão contínua foi aceita em 11/11. O registro cita CI aprovado para a persistência em `69f05a3`. [Consolidação I01](../evidence/I01-consolidacao.md) | Vincular resultados e artefatos ao candidato de G0. Confirmar o CI da ingestão contínua, que constava na fila na revisão histórica, e validar os contratos e as regras de lacunas e correções aplicáveis. |
| I02 · Features e Market State · TS-ST-007/008 | A consolidação registra aceite das três etapas até as features adicionais. Há ensaios de corte temporal, linhagem e alinhamento multi-intervalo. [Consolidação I02](../evidence/I02-consolidacao.md) · [Matriz I01/I02](DOC-03-I01-I02-TRACEABILITY.md) | Identificar as versões e os resultados do candidato. Validar o catálogo e a compatibilidade de features, o recorte SMC aplicável e os critérios explícitos de frescor. |
| I03 · Trading Core PAPER · TS-ST-009–012 | Os registros históricos cobrem controles Spot, persistência, replay, custos, reconciliação e recortes Futures. O checkout oficial contém os caminhos integrados de Market State e seus testes. [Matriz I03](DOC-03-I03-TRACEABILITY.md) · [Arquitetura PAPER](../architecture/trading-core-paper.md) · [Recuperação da marcação](../evidence/I03-recuperacao-marcacao-paper.md) | Vincular os ensaios ao commit e à suite de integração correspondente. Validar os contratos e invariantes aplicáveis e registrar o aceite consolidado de I03 ou suas ressalvas. |
| I04 · AI e Learning · TS-ST-013/014 | I02 fornece evidência das entradas de mercado. I03 fornece casos de risco e simulação. A matriz de I04 não localizou evidência própria de aceite das histórias. [Matriz I04](DOC-03-I04-TRACEABILITY.md) | Demonstrar Observation Builder determinístico e versionado, dataset identificado (P57), treino PPO reproduzível, Registry e inferência rastreável, com preservação da autoridade de Control e Risk. Anexar candidato, versões, testes e resultados. |

## Ressalvas de I00 na abertura do dossiê · 12/11/2026

| Critério | Evidência existente | Pendência de validação |
|---|---|---|
| AC02 · Dependências controladas | RC1 registra instalação com lockfile, build e compatibilidade nos ambientes ensaiados. O lockfile, o manifesto de dependências e o workflow atuais diferem dos do snapshot. | Inventariar dependências resolvidas e insumos de build do candidato, confirmar plataformas e repetir compatibilidade. Anexar auditoria de segurança, tratamento dos achados e parecer dos responsáveis. [DOC-06](DOC-06-RELEASE-DEPENDENCIES.md) |
| AC07 · Ordenação por agregado | Os testes históricos demonstram espera pela versão anterior e avanço de agregados independentes. | Aprovar e testar conflitos de versão, lacunas permanentes, bloqueio, reconciliação e retomada idempotente em PostgreSQL. [DOC-04](DOC-04-OUTBOX-ORDERING.md) |
| AC09 · Observabilidade | Diagnóstico, logs e correlação já têm evidência. | Aprovar as métricas de backlog e atraso e comparar valores esperados e observados por cenário e ambiente no candidato. [DOC-05](DOC-05-OUTBOX-METRICS.md) |

## Decisão humana ainda necessária

1. Engenharia e QA devem confirmar o escopo, as versões candidatas de I00–I04 e os responsáveis pela revisão. Para cada resultado, registrar commit, ambiente, versão de contrato e referência ao CI ou à execução reproduzível.
2. Consolidar a cobertura dos critérios de G0, incluindo build, testes, contratos, invariantes e conformidade arquitetural. Para cada ressalva, registrar evidência de resolução ou decisão formal de tratamento, com justificativa, responsável e prazo.
3. Registrar parecer humano com data, escopo, candidatos, evidências e ressalvas. **Parecer atual: pendente.** O aceite já registrado do RC1 permanece circunscrito ao Evidence Bundle de I00.

A verificação desta consolidação foi documental, com PowerShell, `rg` e conferência dos oito hashes do RC1. Os resultados de testes são históricos.


## Validação de AC02 no candidato d561026

Em 12/11/2026 foi verificado o commit `d561026f27fa3920699af41aeea6e1a60bcf89a6`. O checkout tinha alterações documentais e a comparação com HEAD não mostrou diferenças rastreadas nas áreas de código, testes, dependências, CI e deploy inspecionadas. O inventário registra o SHA-256 local do lockfile e os hashes dos artefatos gerados.

- Windows x64, Python 3.12.12 e uv 0.9.26. A venv existente falhou na coleta por dependências ausentes. Em venv temporária, `uv sync --locked` passou. `pytest` registrou 105 aprovados e 38 pulados, com PostgreSQL desativado na execução. `uv build --no-sources` gerou wheel e sdist.
- A consulta OSV retornou 58 respostas para 58 dependências PyPI instaladas, com zero correspondências para os pares nome/versão consultados. O inventário inclui o grupo de desenvolvimento e confere com as versões do lockfile. A cobertura se limita aos pacotes Python instalados no Windows e aos avisos indexados no instante da consulta.
- Faltam Linux/CI e integração PostgreSQL no mesmo candidato, digest e auditoria da imagem PostgreSQL e avaliação dos componentes nativos e de build fora do inventário Python. Confirmar plataformas suportadas e registrar parecer humano de Engenharia, QA e Segurança.

AC02 permanece em validação. G0 segue aberto. LIVE permanece indisponível.

[Inventário, resultados e hashes de build](../evidence/AC02-d561026.json)

## Complemento de AC02 para d561026

O CI Linux do SHA exato passou, incluindo 38 testes PostgreSQL em PAPER. A imagem atual foi auditada por digest e difere da imagem observada no CI. A identificação do digest histórico, a triagem dos achados e a cobertura nativa e de build restante seguem pendentes. [Evidência Linux e segurança](../evidence/AC02-d561026-linux-security.md)

## Triagem complementar e repetição por digest

O wheel Linux de psycopg-binary foi conferido contra o lockfile. A triagem da imagem identificou libxml2 afetado e documentou a hipótese de baixa aplicabilidade do achado TLS de gosu. A repetição por digest requer runner Linux com Docker. A triagem completa e o inventário do build Linux permanecem pendentes. [Evidência e instruções de repetição](../evidence/AC02-d561026-digest-triage.md)


## Repetição de AC02 com digest fixado

O [workflow manual de AC02](../../.github/workflows/ac02-postgres-digest.yml) está preparado para Linux amd64 com Docker. Ele confere o SHA exato de d561026, instala pelo lockfile e sobrepõe a imagem do Compose com o manifesto auditado. Confere o ID da imagem em execução, registra SHA, hash do lockfile, digest e versão PostgreSQL e executa a suíte de integração em PAPER com LIVE_ENABLED=false. Usa senha de teste mascarada, loopback e volume descartável.

Workflow publicado na branch padrão codex/i00-bootstrap no commit 5c431bb37273c459921ce7000e40135a9df0d615 e disparado manualmente em 12/11/2026. O job testou o candidato d561026f27fa3920699af41aeea6e1a60bcf89a6 em Linux amd64 com PostgreSQL 17.12 (Debian 17.12-1.pgdg13+1) e digest sha256:6f7593c161689b6b02c78668b314af7da8811b592c5519108c57a49d0b6ad788. O SHA-256 do lockfile conferiu com e40093ac899ba45d0d9290942cb66553fc02722d55f7cceeba70f26713970919. Resultado: **38 testes aprovados em 7,43 s**, com PAPER e LIVE_ENABLED=false. O log confirma remoção do container, da rede e do volume. [Execução 43324339962, job 131552874577](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43324339962/job/131552874577)

 A imagem fixada contém achados em aberto. A triagem de aplicabilidade e o parecer sobre uso no recorte isolado permanecem pendentes. Também faltam as versões e a procedência dos componentes nativos Linux, a confirmação dos pacotes resolvidos no build isolado Linux, a avaliação de avisos e o parecer humano de Engenharia, QA e Segurança. [Triagem e relatório](../evidence/AC02-d561026-digest-triage.md)

AC02 segue em validação, G0 segue aberto e LIVE permanece indisponível.

Os [critérios de aceite de AC02](AC02-ENGINEERING-ACCEPTANCE.md) foram aprovados pelo usuário em 12/11/2026. O [repasse a Engenharia](AC02-ENGINEERING-HANDOFF.md) está pronto. O aceite de AC02 aguarda evidências e parecer humano.

## Retorno parcial de Engenharia sobre AC02

Em 16/11/2026, TS-DOC-GOV incorporou o [retorno de 13/11](../evidence/AC02-d561026-retorno-engenharia.md) para o candidato d561026 e o digest 6f7593c. Os 38 testes PostgreSQL aprovados por digest já constam do log verificado anteriormente. O erro 403 relatado por Engenharia limita o acesso ao log naquela revisão.

- A [triagem CSV](../evidence/AC02-d561026-postgres-triage.csv) registra 610 ocorrências. Faltam confirmar aplicabilidade e alcance e registrar as correções ou exceções decididas por Segurança.
- O [inventário estático](../evidence/AC02-d561026-linux-wheel-static.json) registra hashes de 17 arquivos ELF, incluindo 15 bibliotecas. Faltam evidências de seleção e carregamento no runner, versões efetivas, backports e análise dos avisos aplicáveis.
- O build Linux passou no CI. Ainda faltam o inventário e a auditoria das dependências efetivamente resolvidas no build isolado e os logs e hashes dos artefatos correspondentes.

Os critérios foram aprovados em 12/11. **AC02 permanece em validação, G0 segue aberto e LIVE permanece indisponível.**

## Aprovação documental de DOC-04 e DOC-05

Em 16/11/2026 o usuário aprovou nesta conversa a [política de ordenação da Outbox](DOC-04-OUTBOX-ORDERING.md) e as [definições de métricas](DOC-05-OUTBOX-METRICS.md). Engenharia deve demonstrar AC07 e AC09 em PostgreSQL e devolver os resultados vinculados ao candidato. Parâmetros ainda abertos e aceite técnico dependem das evidências e da revisão humana. G0 segue aberto e LIVE permanece indisponível.

## Retorno de Engenharia sobre AC07 e AC09

Em 16/11/2026, Engenharia concluiu os ensaios no candidato `11e61c9a0875ed91ba68788063364f4dec44dfca`, em PostgreSQL 17.11 descartável, Windows, loopback e `LIVE_ENABLED=false`. O escopo foi PAPER para AC07 e PAPER/TRAINING para AC09. TS-DOC-GOV conferiu os registros e seus vínculos. As propostas DOC-04 e DOC-05 continuam aprovadas e o aceite técnico permanece pendente.

| Critério | Resultado | Para aceite |
|---|---|---|
| AC07 · aberto | Oito testes aprovados e 31 desmarcados. O ensaio cobriu espera por predecessor, progresso de agregados independentes, retomada em ordem e efeito único no replay. A sonda concorrente gravou e publicou dois eventos com IDs distintos para a mesma versão. [Evidência AC07](../evidence/AC07-11e61c9-outbox.md) | Confirmar cardinalidade com os produtores e tratar dados existentes. Demonstrar detecção de conflito sob concorrência, evidência durável após rollback, quarentena, predecessor removido por retenção e reparo com reinício e retomada autorizada. Definir fonte autoritativa, responsáveis, limiar e retenção. |
| AC09 · parcial | A consulta de referência conferiu a precedência das categorias, idade preservada após retry, queda do backlog PAPER de 3 para 2 após publicação, segregação de TRAINING e distinção entre fila vazia e conexão indisponível. O ensaio de atraso usou o histórico sintético inteiro. [Evidência AC09](../evidence/AC09-11e61c9-outbox.md) | Demonstrar o coletor do produto, publicação do estado de indisponibilidade, distribuição com janela explícita e contagens deduplicadas por intervalo. Aprovar frequência, janela, limiares, relógio de alerta e responsáveis. Repetir a validação com o coletor implementado. |

Engenharia e QA devem devolver os resultados reproduzíveis vinculados ao candidato resultante e o parecer para a decisão humana. G0 segue aberto. LIVE permanece indisponível.

## Implementação e validação incremental de AC07 e AC09

Em 16/11/2026, Engenharia entregou os dois pacotes no checkout oficial. O código testado tem base 11e61c9a0875ed91ba68788063364f4dec44dfca e alterações locais AC07 e AC09. Os testes usaram PostgreSQL 17.11 descartável em loopback, Windows, credenciais de teste e LIVE_ENABLED=false. AC07 foi exercitado em PAPER e AC09 em PAPER e TRAINING. TS-DOC-GOV conferiu os registros e os oito SHA-256 do inventário do código e lockfile testados. As contagens refletem duas execuções sucessivas de Engenharia.

| Critério | Evidência entregue | Para aceite |
|---|---|---|
| AC07 · parcial | A migração 0016 impõe unicidade por versão e escopo do agregado, inclusive sem conta. No teste concorrente, um produtor confirmou estado e evento e o outro sofreu rollback. O incidente seguiu consultável e outra conta publicou. Engenharia registrou 145 testes aprovados e sucesso em Ruff e mypy. [Evidência da correção](../evidence/AC07-conflito-concorrente-outbox.md) | Confirmar cardinalidade dos produtores operacionais e decidir a reconciliação de dados legados em conflito. Demonstrar quarentena durável por agregado, tratamento de predecessor removido ou retido, reparo com reinício e liberação autorizada após reconciliação, inclusive de conflito já publicado. Confirmar a autoridade, a fonte e os parâmetros operacionais. |
| AC09 · coletor validado em integração, aceite pendente | O coletor e a migração 0017 foram testados no mesmo snapshot com janela explícita. O backlog caiu de 4 para 2 após publicação, as contagens se mantiveram em coletas repetidas, e o estado unavailable distinguiu falha de fila vazia. Engenharia registrou 146 testes aprovados e sucesso em lint, formatação e mypy. [Evidência do coletor](../evidence/AC09-coletor-outbox.md) · [Hashes](../evidence/AC09-outbox-metrics-sha256.txt) | Aprovar frequência, janela, limiares, retenção, tratamento de timestamps inconsistentes e responsáveis. A duração desde a detecção de bloqueio depende do marco de DOC-04. |

As propostas documentais seguem aprovadas. Para a decisão de aceite, associar as evidências ao candidato que será submetido à revisão e registrar o parecer de Engenharia e QA, com escopo e ressalvas. G0 permanece aberto e LIVE permanece indisponível.


## Consolidação de AC07 para revisão técnica

O retorno de Engenharia reúne os cenários validados e as pendências de aceite técnico. Os 16 hashes do último ensaio foram reconferidos. G0 segue aberto e LIVE permanece indisponível. [Consolidação AC07](../evidence/AC07-consolidacao-aceite-tecnico.md)


## Candidato de AC07 e pendências de validação

**16/11/2026 · Revisão técnica pendente.** Candidato local
`184e8b30a8dc9d812bce092e893f70a8931c4570`. Contém as migrações
`0016`–`0022`, a dependência de tentativas e métricas de AC09, e
a trilha de ensaios de AC07. O tratamento do mesmo `event_id` com
conteúdo divergente está incluído.
[Evidências do conflito](../evidence/AC07-event-id-divergente.md)

| Pendência | O que fecha a pendência | Responsável funcional |
|---|---|---|
| Confirmação com produtores | Identificar os produtores operacionais, obter confirmação de um evento por versão e registrar a fonte que preserva o envelope original de cada produtor. | Engenharia e responsáveis pelos produtores |
| Análise do snapshot legado | Identificar um snapshot autorizado anterior à revisão `0016` e executar a pré-checagem somente leitura. Registrar origem, ambiente e contagens. Se houver colisões ou versões incompatíveis, reconciliar com decisão registrada e repetir a consulta. | Administração do banco, Engenharia e QA |

A consulta já foi aprovada e validada com um fixture sintético no
PostgreSQL. Nenhum snapshot legado real foi disponibilizado para
análise nesta revisão.
[Pré-checagem e evidência](../evidence/AC07-produtores-e-colisoes-legadas.md)

O aceite técnico de AC07 depende da revisão de Engenharia e QA e
da decisão humana sobre as pendências. LIVE permanece indisponível
e G0 segue aberto.

A validação a partir de `git archive` do commit candidato passou com **153 testes** em PostgreSQL 17.11 descartável, PAPER e `LIVE_ENABLED=false`. Ruff, formatação e mypy também passaram. O ensaio não abrangeu o snapshot legado real.
