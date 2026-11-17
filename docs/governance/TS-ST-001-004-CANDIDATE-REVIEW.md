# Composição completa do candidato TS-ST-001–004

Estado IN_REVIEW. Data 17/11/2026. Repositório de trabalho: DeepTradeSystem do BUSINESS.

Base herdada: 184e8b30a8dc9d812bce092e893f70a8931c4570. A composição acrescenta 302 arquivos novos ou modificados. Inclui documentos de apoio por referências locais transitivas; documentos históricos entram como evidência arquivada, sem expandir os links copiados do local original.

[Manifesto exato dos arquivos a acrescentar ao commit](TS-ST-001-004-CANDIDATE-FILES.txt) · [Auditoria dos 204 destinos históricos](TS-ST-001-004-LINK-AUDIT.md)

| Conjunto | Arquivos |
|---|---|
| ADRs e índice | 99 |
| Evidências complementares | 8 |
| Features e apoio referenciado | 14 |
| Fontes e proveniência | 10 |
| Governança e rastreabilidade | 35 |
| Histórias e registro mestre | 5 |
| Históricos de aprovação e revisão | 107 |
| Outros documentos de apoio | 9 |
| Templates aprovados | 15 |

## Conferência da composição

Foram verificadas a existência de todos os caminhos e as referências locais dos documentos atuais alcançados a partir das histórias, matriz, índice de ADRs, Approval Register e fontes oficiais. Ocorrências atuais de destino ausente: 0. A auditoria anterior classificou os 204 destinos como históricos.

O índice das 98 ADRs inclui fichas de todos os domínios. Registros globais de governança e catálogos de I00 também referenciam documentação de outros incrementos; os arquivos alcançados entram como apoio documental. Essa inclusão preserva as referências atuais e seus estados existentes.

## Arquivos já herdados da base

Os 96 caminhos abaixo já estão presentes no conteúdo de base e são consultados pela composição. Seu conteúdo é herdado pelo próximo commit.

- .github/workflows/ci.yml
- apps/market_data/paper.py
- contracts/examples/command-envelope.example.json
- contracts/examples/event-envelope.example.json
- contracts/jsonschema/command-envelope.v1.schema.json
- contracts/jsonschema/event-envelope.v1.schema.json
- docs/00-BASELINE-E-ESCOPO.md
- docs/01-ARQUITETURA-FISICA.md
- docs/02-I00-BACKLOG.md
- docs/03-CONTRATOS.md
- docs/04-SEGURANCA-E-ACEITE.md
- docs/05-ADRS-TECNICAS.md
- docs/evidence/AC07-11e61c9-outbox.md
- docs/evidence/AC07-autorizacao-outbox.md
- docs/evidence/AC07-autorizacao-sha256.txt
- docs/evidence/AC07-conflito-concorrente-outbox.md
- docs/evidence/AC07-consolidacao-aceite-tecnico.md
- docs/evidence/AC07-dispatcher-login-restrito.md
- docs/evidence/AC07-dispatcher-login-sha256.txt
- docs/evidence/AC07-escalonamento-predecessor.md
- docs/evidence/AC07-escalonamento-sha256.txt
- docs/evidence/AC07-event-id-divergente.md
- docs/evidence/AC07-event-id-sha256.txt
- docs/evidence/AC07-parametros-operacionais.md
- docs/evidence/AC07-parametros-sha256.txt
- docs/evidence/AC07-produtores-e-colisoes-legadas.md
- docs/evidence/AC07-quarentena-retomada.md
- docs/evidence/AC07-quarentena-sha256.txt
- docs/evidence/AC09-11e61c9-outbox.md
- docs/evidence/AC09-coletor-outbox.md
- docs/evidence/AC09-outbox-metrics-sha256.txt
- docs/evidence/I00-03-contratos.md
- docs/evidence/I00-04-postgresql.md
- docs/evidence/I00-05-outbox.md
- docs/evidence/I00-06-dispatcher.md
- docs/evidence/I00-07-consumidor.md
- docs/evidence/I00-08-api.md
- docs/evidence/I00-09-isolamento.md
- docs/evidence/I00-10-telemetria.md
- docs/evidence/I00-12-rastreabilidade.md
- docs/evidence/I00-13-resiliencia.md
- docs/evidence/I00-bootstrap.md
- docs/evidence/I01-consolidacao.md
- docs/evidence/I01-historico-btcusdt.md
- docs/evidence/I01-ingestao-continua-btcusdt.md
- docs/evidence/I01-persistencia-btcusdt.md
- docs/evidence/I02-consolidacao.md
- docs/evidence/I02-features-adicionais.md
- docs/evidence/I02-market-state-inicial.md
- docs/evidence/I02-market-state-multi-intervalo.md
- docs/evidence/I03-custos-paper.md
- docs/evidence/I03-funding-paper.md
- docs/evidence/I03-futures-paper.md
- docs/evidence/I03-liquidacao-paper.md
- docs/evidence/I03-market-state-paper.md
- docs/evidence/I03-persistencia-paper.md
- docs/evidence/I03-recuperacao-marcacao-paper.md
- docs/evidence/releases/i00-rc1/diagnostic-log.json
- docs/evidence/releases/i00-rc1/manifest.json
- docs/evidence/releases/i00-rc1/README.md
- docs/evidence/releases/i00-rc1/SHA256SUMS
- docs/evidence/releases/i00-rc1/test-results.json
- docs/governance/DOC-04-OUTBOX-ORDERING.md
- docs/governance/DOC-05-OUTBOX-METRICS.md
- docs/runbooks/api-diagnostico.md
- docs/runbooks/consumidor-idempotente.md
- docs/runbooks/dispatcher-outbox.md
- docs/runbooks/historico-btcusdt.md
- docs/runbooks/ingestao-continua-btcusdt.md
- docs/runbooks/isolamento-e-segredos.md
- docs/runbooks/market-state-btcusdt.md
- docs/runbooks/outbox-transacional.md
- docs/runbooks/paper-futures.md
- docs/runbooks/paper-livro-razao.md
- docs/runbooks/paper-market-state.md
- docs/runbooks/paper-simulacao-inicial.md
- docs/runbooks/paper-taxas-e-slippage.md
- docs/runbooks/postgresql-local.md
- docs/runbooks/telemetria-local.md
- infrastructure/database/paper_futures.py
- infrastructure/database/paper_ledger.py
- infrastructure/events/dispatcher.py
- infrastructure/events/outbox.py
- pyproject.toml
- src/trade_system/control/paper.py
- src/trade_system/risk/paper.py
- tests/contracts/test_envelope_schemas.py
- tests/integration/test_postgres_migrations.py
- tests/unit/test_diagnostic_api.py
- tests/unit/test_local_security.py
- tests/unit/test_market_history.py
- tests/unit/test_market_state.py
- tests/unit/test_market_stream.py
- tests/unit/test_package_imports.py
- tests/unit/test_paper_simulator.py
- uv.lock

## Arquivos pendentes fora da composição

- .github/workflows/ac02-postgres-digest.yml
- docs/architecture/visao-inicial.md
- docs/governance/history/TS-DOC-APR-001/REGISTRO-LOCAL-ANTERIOR.txt
- docs/referencias/Architecture & MVP Blueprint.txt
- docs/referencias/Binance API Integration.txt
- docs/referencias/Domínio 01 - Integração e Dados de Mercado.txt
- docs/referencias/Domínio 02 - Inteligência Artificial e Aprendizado.txt
- docs/referencias/Domínio 03 - Risco, Execução e Controle Operacional.txt
- docs/referencias/Domínio 04 - Plataforma de Operações e Observabilidade.txt
- docs/referencias/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt
- docs/referencias/Domínio 06 · Infraestrutura, Segurança e DevOps.txt
- docs/referencias/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt
- docs/referencias/Trading Operations Viewer.txt
- docs/referencias/TS-ENG-I00-V1.0 - Engineering Foundation.txt
- docs/runbooks/revisao-vscode.md
- docs/TS-DOC-STD-V1.0.txt

As oito remoções dos DOCX permanecem fora desta composição; a migração documental pode ser registrada em alteração própria. O workflow AC02 por digest fixa d561026 e exige ajuste específico para verificar o candidato final.

## Verificações posteriores

Após a decisão sobre a composição, identificar o SHA resultante e executar as verificações dos 20 critérios sobre esse candidato. Reconfirmar métricas devido às três divergências do manifesto histórico. Responsáveis técnico, QA e operadores aguardam designação.

## Referências atuais com destino ausente

A conferência de existência dos destinos locais atuais alcançados terminou sem ocorrências.
