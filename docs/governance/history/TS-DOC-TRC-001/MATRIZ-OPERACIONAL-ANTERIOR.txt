# Matriz de rastreabilidade de requisitos

Auditoria TS-DOC-GOV de 12/11/2026. Versão DRAFT. AC indica critério de [aceite I00](../04-SEGURANCA-E-ACEITE.md). Os work packages vêm do [backlog I00](../02-I00-BACKLOG.md). ADRs técnicas e testes foram associados a partir do [registro mestre](../backlog/registro-mestre-i00.md). T09 é uma decisão técnica citada nesse registro. A coluna componente usa nomes locais ou a fronteira de domínio quando o vínculo histórico por ID não está demonstrado. Resultados são históricos, conforme a [revisão RC1](../evidence/revisao-g0-i00-rc1.md).

| Origem | Requisito e critério | Componente | Contrato ou artefato | Pacote | Verificação | Evidência |
|---|---|---|---|---|---|---|
| ADR-089, 090, 098 | Instalação e estrutura modular isolada · AC01, AC10 | Monorepo | Pacote Python | I00-01 | Smoke de imports | [Bootstrap](../evidence/I00-bootstrap.md) |
| ADR-094 | Dependências fixadas e build repetível · AC01, AC02 | Toolchain | uv.lock | I00-02 | Instalação locked, build e qualidade | [Bootstrap](../evidence/I00-bootstrap.md) |
| ADR-097, 098 | Validar envelopes e ambientes permitidos · AC03, AC10 | D05 · eventos | [Command](../../contracts/jsonschema/command-envelope.v1.schema.json) e [Event](../../contracts/jsonschema/event-envelope.v1.schema.json) | I00-03 | [Testes de schema](../../tests/contracts/test_envelope_schemas.py) | [Contratos](../evidence/I00-03-contratos.md) |
| ADR-092, 095 | Migrações reversíveis · AC04 | D05 · PostgreSQL | Alembic | I00-04 | test_migrations_round_trip | [PostgreSQL](../evidence/I00-04-postgresql.md) |
| ADR-092, 093 | Estado e evento na mesma transação · AC05, AC08 | D05 · Outbox | EventEnvelope e registro persistido | I00-05 | Commit, rollback e evento duplicado | [Outbox](../evidence/I00-05-outbox.md) |
| ADR-090, 093, 096 | Ordem por agregado e retry · AC07, AC08, AC09 | Dispatcher | EventEnvelope e Outbox | I00-06 | Ordem de versões pendentes, retry, retomada | [Dispatcher](../evidence/I00-06-dispatcher.md) · DOC-04 |
| ADR-090, 093 | Efeito único após replay · AC06, AC08 | Consumidor | EventEnvelope, deduplicação transacional | I00-07 | Replay entre processos e rollback | [Consumidor](../evidence/I00-07-consumidor.md) |
| ADR-091, 097, 098 | Saúde, prontidão e informações locais · AC09, AC10 | API | OpenAPI gerado em runtime | I00-08 | [Testes da API](../../tests/unit/test_diagnostic_api.py) e prontidão com PostgreSQL | [API](../evidence/I00-08-api.md) |
| ADR-098 | Fail-closed, isolamento e LIVE inacessível · AC10 | Configuração e workers | Ambientes TRAINING/PAPER | I00-09 | [Testes de configuração](../../tests/unit/test_local_security.py) e rejeição no PostgreSQL | [Isolamento](../evidence/I00-09-isolamento.md) |
| ADR-096 | Logs JSON e correlação entre processos · AC09 | Telemetria | correlation_id no envelope e nos logs | I00-10 | Correlação API, dispatcher e consumidor | [Telemetria](../evidence/I00-10-telemetria.md) · DOC-05 |
| ADR-095 | CI de qualidade e build · AC01, AC02 | CI | [Workflow](../../.github/workflows/ci.yml) | I00-11 | Ruff, mypy, pytest e build em CI histórico | [Resultados RC1](../evidence/releases/i00-rc1/test-results.json) |
| T09 | Rastrear pacotes e evidências · AC11 | Governança | Registro mestre | I00-12 | Revisão de IDs e referências | [Rastreabilidade](../evidence/I00-12-rastreabilidade.md) · DOC-01–03 |
| ADR-093, 094 | Recuperação, chegada tardia e reinício · AC07, AC08 | Outbox, dispatcher, consumidor | EventEnvelope e checkpoints locais | I00-13 | Falhas, retry, retomada e chegada posterior da versão faltante | [Resiliência](../evidence/I00-13-resiliencia.md) · DOC-04 |
| T09 | Bundle verificável e decisão de aceite · AC11, AC12 | Release e QA | Manifesto, resultados, checksums | I00-14 | Verificação histórica de oito hashes | [Revisão e aceite de RC1](../evidence/revisao-g0-i00-rc1.md) · [oito hashes conferidos em 12/11](SOURCE-RECOVERY.md) |

A matriz mapeia 14 de 14 pacotes e 12 de 12 critérios de I00. A revisão de RC1 considera AC07 e AC09 parciais e registra ressalva em AC02. Esses números medem presença de vínculo. A cobertura dos originais G01–G60, ADR-001–088, P01–P106 e das histórias globais é indeterminada. A execução e o aceite de cada critério exigem evidência própria.

## Mapa global para recuperação das fontes

| Domínio e componentes presentes nas fontes oficiais | Faixa ADR | Pendências | Fluxos citados no domínio | Ponto de partida |
|---|---|---|---|---|
| D01-C01–C03 | 001–006 | P01–P08 | F01, F02 | [D01](<../referencias/originais/Domínio 01 - Integração e Dados de Mercado.txt>) · [I01](../evidence/I01-consolidacao.md) · [I02](../evidence/I02-consolidacao.md) |
| D02-C01–C03 | 007–016 | P09–P18 | F02, F07 | [D02](<../referencias/originais/Domínio 02 - Inteligência Artificial e Aprendizado.txt>) |
| D03-C01–C04 | 017–028 | P19–P32 | F03–F06, F08 | [D03](<../referencias/originais/Domínio 03 - Risco, Execução e Controle Operacional.txt>) · [I03](../evidence/I03-futures-paper.md) |
| D04-C01–C05 | 029–040 | P33–P47 | F06, F08, F09 | [D04](<../referencias/originais/Domínio 04 - Plataforma de Operações e Observabilidade.txt>) |
| D05-C01–C06 | 041–054 | P48–P64 | F01–F10 | [D05](<../referencias/originais/Domínio 05 - Plataforma de Dados, Eventos e Auditoria.txt>) |
| D06-C01–C06 | 055–070 | P65–P84 | F07, F10 | [D06](<../referencias/originais/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>) |
| D07-C01–C06 | 071–088 | P85–P106 | F01–F10 | [D07](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>) |

As faixas localizam as fontes por domínio. Há registros por ID para [P01–P106](PENDING-ITEM-RECONCILIATION.md) e [ADR-001–098](ADR-RECONCILIATION.md). A [matriz DOC-03 de I00](DOC-03-I00-TRACEABILITY.md) liga quatro histórias e 14 pacotes ao RC1. A [matriz de I01 e I02](DOC-03-I01-I02-TRACEABILITY.md) cobre TS-ST-005–008 e o recorte de P56 e P57. A [matriz de I03](DOC-03-I03-TRACEABILITY.md) cobre TS-ST-009–012 e o Trading Core PAPER. A [matriz de I04](DOC-03-I04-TRACEABILITY.md) cobre TS-ST-013/014, incluindo P56 e P57. A [matriz de I05](DOC-03-I05-TRACEABILITY.md) cobre TS-ST-015/016, incluindo P57 e os critérios de G1. A [matriz de I06](DOC-03-I06-TRACEABILITY.md) cobre TS-ST-017–020 e as condições pendentes de G2. A [matriz de I07](DOC-03-I07-TRACEABILITY.md) cobre TS-ST-021/022 e as condições pendentes de G3. A [matriz de I08](DOC-03-I08-TRACEABILITY.md) cobre TS-ST-023 e as condições pendentes de G4. A [matriz de I09](DOC-03-I09-TRACEABILITY.md) cobre TS-ST-024 e as condições pendentes de G5. A validação dos vínculos propostos segue aberta.

[Consolidação DOC-03 de I00 a I09 e validações de G0 a G5](DOC-03-CONSOLIDATION.md).


## Atualização de rastreabilidade · 16/11/2026

As linhas históricas acima conservam o recorte de RC1. Os retornos abaixo têm identidade própria e o aceite de G0 segue pendente. Os vínculos globais posteriores estão na [consolidação DOC-03](DOC-03-CONSOLIDATION.md), incluindo as matrizes de I00 a I09.

| Origem / critério | História e pacote | Contrato ou superfície | Verificação e evidência | Decisão ou lacuna |
|---|---|---|---|---|
| TS-ADR-094/095 · I00-AC02 | [DOC-03 I00](DOC-03-I00-TRACEABILITY.md) · I00-02, I00-11 | Lockfile, imagem PostgreSQL, componentes nativos e build Linux | [Repetição por digest e triagem](../evidence/AC02-d561026-retorno-engenharia.md) | [Critérios aprovados](AC02-ENGINEERING-ACCEPTANCE.md). Parecer e evidência complementar pendentes. |
| TS-ADR-093 · DOC-04 · I00-AC07 | [DOC-03 I00](DOC-03-I00-TRACEABILITY.md) · I00-06, I00-13 | EventEnvelope, Outbox e ordem por agregado | [Conflito por ID](../evidence/AC07-event-id-divergente.md) · [153 testes no candidato](G0-REVIEW-DOSSIER.md) | Política aprovada. Produtores, legado e aceite pendentes. |
| TS-ADR-096 · DOC-05 · I00-AC09 | [DOC-03 I00](DOC-03-I00-TRACEABILITY.md) · I00-06, I00-10, I00-13 | Diagnóstico e métricas da Outbox | [Teste do coletor PostgreSQL](../evidence/AC09-coletor-outbox.md) | Definições aprovadas. Aceite e parâmetros pendentes. |
| DOC-07 · I00-AC12 | [DOC-03 I00](DOC-03-I00-TRACEABILITY.md) · I00-14 | Manifesto e checksum | [Bundle RC1](../evidence/releases/i00-rc1/README.md) | [Aceite RC1](DOC-07-RC1-ACCEPTANCE.md). G0 pendente. |

Consulte o [Gap Register](GAP-REGISTER.md) e o [Approval Register](APPROVAL-REGISTER.md) para as ações e decisões, respectivamente.

