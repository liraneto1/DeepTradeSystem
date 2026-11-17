# Lacunas documentais do Trade System V1

Auditoria TS-DOC-GOV de 12/11/2026. Versão DRAFT. A fundação I00 tem backlog, contratos executáveis e evidências históricas. A completude documental de I00 e dos demais incrementos ainda requer validação humana. A [revisão de 11/11](../evidence/revisao-g0-i00-rc1.md) registra aceite de I00-14 e do bundle RC1. G0 segue aberto.

| Referência | Achado | Impacto | Ação e evidência esperada |
|---|---|---|---|
| RC1 | Bundle original recuperado. Oito hashes conferiram, e o ZIP identifica o commit candidato. | Integridade dos arquivos verificada localmente. | A referência Git de publicação ainda depende de histórico acessível. [Recuperação](SOURCE-RECOVERY.md) |
| DOC-04 · AC07 | I00-13 registra chegada tardia recuperável. Versões conflitantes e lacunas permanentes seguem sem política decidida. | Cobertura parcial do aceite de ordenação. | Aprovar a [política proposta](DOC-04-OUTBOX-ORDERING.md) e validar os cenários pendentes. [Resiliência](../evidence/I00-13-resiliencia.md) |
| DOC-05 · AC09 | Diagnóstico e correlação têm evidência. Backlog e atraso ainda carecem de evidência. | Cobertura parcial de observabilidade. | Revisar as [definições propostas](DOC-05-OUTBOX-METRICS.md) e registrar a medição no candidato. [Telemetria](../evidence/I00-10-telemetria.md) |
| DOC-06 · AC02 | Lockfile e instalação controlada existem. Avaliação de compatibilidade e segurança de release e responsáveis seguem em aberto. | Limita conclusão sobre a release. | Revisar a [avaliação documental](DOC-06-RELEASE-DEPENDENCIES.md) e anexar inventário, resultados de segurança e decisão ao candidato. [Revisão](../evidence/revisao-g0-i00-rc1.md) |
| DOC-07 · AC12 e G0 | O aceite humano do RC1 está consolidado. O manifesto conserva o estado histórico anterior à decisão. | AC12 evidenciado no escopo do RC1. G0 aberto. | Reunir evidências de I00–I04, tratar ressalvas e registrar a decisão humana. [DOC-07](DOC-07-RC1-ACCEPTANCE.md) |
| Contratos I00 | Dois envelopes têm schemas e testes. OpenAPI está disponível em runtime segundo as evidências. ErrorEnvelope.v1, HealthStatus.v1 e OutboxRecord.v1 são propostas sem artefato individual versionado localizado. | Obrigatoriedade de cada artefato ainda precisa de confirmação. | Aprovar catálogo I00, identificando definição, versão e verificação exigidas. [Contratos](../03-CONTRATOS.md) |
| DOC-01 e DOC-02 | Descrições e fases primárias vinculadas às fontes para P01–P106. P18 permanece M3 provisório. | A etapa de confronto de DOC-01 está coberta. DOC-02 permanece aberto. | Revisar as ressalvas documentadas e registrar eventual mudança conforme G40. [Decisões pendentes](RECONCILIATION-DECISIONS.md) |
| DOC-03 | G01–G60 aparecem agrupadas. Há 33 componentes nomeados e 10 fluxos nomeados. Falta a cadeia global por decisão, pendência, história, contrato e evidência. Os 14 pacotes I00 são verificáveis no backlog local. | Completude global indeterminada. | Recuperar G01–G60, ADRs 001–088, inventário P01–P106 e catálogo dos 14 épicos e 24 histórias iniciais. [Escopo](../00-BASELINE-E-ESCOPO.md) |
| ADR-089–098 | Resumos aprovados disponíveis. Engineering Foundation original recuperado. A cobertura de motivações, alternativas e consequências requer conferência por ADR. | Formalização individual depende dos registros de decisão. | Conciliar com o Engineering Foundation e identificar atas adicionais, se necessárias. [ADRs técnicas](../05-ADRS-TECNICAS.md) |
| G0 | A revisão cita critérios de originais ausentes do checkout e pede evidências de I01–I04. Há recortes aceitos em I01 e I02 e evidência técnica de I03. | G0 aguarda composição e decisão humana. | Recuperar fontes, rastrear recortes a um candidato, verificar CI e registrar decisão por escopo. [Revisão](../evidence/revisao-g0-i00-rc1.md) |

## Requisitos cuja origem ainda precisa ser confirmada

- A visão inicial registra 30% líquidos ao mês como hipótese de negócio. Falta origem normativa e critério aprovado para uso como meta de aceite.
- Os limites quantitativos dos gates, a decisão final sobre P18 e a política de versões conflitantes dependem de fonte ou decisão explícita.
- Os parâmetros dos ensaios PAPER, incluindo taxas e slippage, são insumos de teste até que a fonte normativa aplicável seja identificada. [Evidência PAPER](../evidence/I03-futures-paper.md)

As lacunas acima qualificam a prontidão documental e o alcance da evidência. A aprovação histórica do bundle mantém o escopo registrado em 11/11.
