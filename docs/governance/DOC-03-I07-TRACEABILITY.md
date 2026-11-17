# Rastreabilidade DOC-03 para I07

**12/11/2026 · IN_REVIEW.** O Blueprint liga TS-ST-021 a TS-EP-11 e P65–P84. O critério da história é segregação e autorização verificadas. O épico acrescenta menor privilégio, restauração e OperationalReadiness. As associações por controle abaixo são propostas de refinamento. TS-ST-022 pertence a TS-EP-12 e tem rastreabilidade própria nesta matriz. LIVE permanece indisponível.

- [Blueprint original](<../referencias/originais/TS-ARCH-GLOBAL-V1.0 - Architecture & MVP Blueprint.txt>) · [D06 original](<../referencias/originais/Domínio 06 · Infraestrutura, Segurança e DevOps.txt>) · [D07 original](<../referencias/originais/Domínio 07 - Engenharia, Qualidade e Validação Operacional.txt>)
- [Pendências por ID](PENDING-ITEM-RECONCILIATION.md) · [ADRs por ID](ADR-RECONCILIATION.md) · [Dependências de I06](DOC-03-I06-TRACEABILITY.md)

| Recorte de TS-ST-021 | Pendências e ADRs | Evidência disponível e validação necessária |
|---|---|---|
| IAM e segregação | P66, P69, P71 · ADR-058/060/068, TS-ADR-098 | `test_workers_process_only_their_environment` e `test_postgres_rejects_live_events` sustentam isolamento lógico local. Aprovar matriz de acesso por ambiente, identidades humanas e de serviço, MFA, RBAC, menor privilégio e segregação de funções. Demonstrar permissões e recusas com identidades de teste. [Isolamento I00](../evidence/I00-09-isolamento.md) |
| Secrets | P70, P80 · ADR-059/060/068, TS-ADR-098 | `test_database_url_is_local_and_masks_password` cobre mascaramento de senha na URL local. Aprovar fonte, responsáveis, fronteiras de acesso, rotação, revogação e trilha de auditoria. Demonstrar falha segura e proteção de logs com segredos sintéticos. [Runbook](../runbooks/isolamento-e-segredos.md) |
| Infraestrutura, release e observabilidade | P65, P67, P68, P72, P73, P74, P75, P76, P81, P83 · ADR-056/057/061–065/069 | RC1 registra CI e build, e I00 documenta correlação. Identificar ambiente e candidato de referência, aprovar topologia, capacidade, reinício, trilha de release, proteção durante mudanças, métricas, alertas, SLOs e controle de drift. A evidência histórica cobre a fundação local. [Resultados RC1](../evidence/releases/i00-rc1/test-results.json) · [Telemetria](../evidence/I00-10-telemetria.md) |
| Backup, DR e reconciliação | P77, P78, P79, P84 · ADR-027/066/067/081 | I01 registra a restauração de uma amostra de mercado. `test_workers_restart_after_database_connection_failure` e `test_paper_fill_survives_process_restart_and_reconciles` exercitam recuperação local. Aprovar retenção, RPO e RTO. Executar restore isolado, medir perda e tempo, verificar consistência e demonstrar retomada condicionada à reconciliação. [Restore I01](../evidence/I01-persistencia-btcusdt.md) · [Resiliência I00](../evidence/I00-13-resiliencia.md) · [Reconciliação I03](../evidence/I03-persistencia-paper.md) |
| OperationalReadiness | P75, P76, P79, P82, P84 · ADR-064/067/070/082 | `test_api_readiness_requires_current_migrations` e `test_readiness_handles_connection_failure` cobrem diagnóstico local do banco. Aprovar schema e versão do contrato, validade da decisão, condições de bloqueio, responsáveis e retomada. Demonstrar em PAPER o tratamento de evidência ausente, vencida ou inconsistente. [Diagnóstico I00](../evidence/I00-08-api.md) |

### Vínculos transversais com persistência e operação do banco

- **P62 · TS-ST-021 · ADR-054/066:** a restauração da amostra de TS-ST-006 é evidência parcial. Faltam política de retenção, RPO/RTO aprovados e exercício de restauração com medições e reconciliação por candidato. [Persistência I01](../evidence/I01-persistencia-btcusdt.md)
- **P64 · TS-ST-021 · ADR-042/064/065:** a persistência de TS-ST-006 e o diagnóstico local servem como referência funcional. Faltam responsáveis, metas de desempenho e crescimento, telemetria do banco e ensaio de capacidade no ambiente de referência. [Matriz I01/I02](DOC-03-I01-I02-TRACEABILITY.md)

## TS-ST-022 · Homologação do Binance Execution Adapter

O Blueprint vincula TS-ST-022 a TS-EP-12, com dependências de TS-EP-06, TS-EP-10 e TS-EP-11. A história exige evidência de timeout, filtros, status e reconciliação. O épico lista P29–P32, P99 e P106. P21–P23, P82 e P96 são vínculos propostos por conteúdo. A revisão aqui é documental. Os cenários de validação descritos para o recorte atual usam PAPER ou respostas sintéticas isoladas, sem ordens reais. LIVE permanece indisponível.

| Critério da história | Pendências e ADRs relacionadas | Evidência disponível e lacuna |
|---|---|---|
| Timeout e resultado incerto | P22/P29/P30/P32 · ADR-021/026/027/081 | `test_workers_restart_after_database_connection_failure` cobre reinício de workers locais. `test_paper_fill_survives_process_restart_and_reconciles` cobre replay e reconciliação após reinício em PAPER. Falta validar timeout antes e depois de um efeito simulado, preservação do estado incerto, bloqueio de reenvio até reconciliação e ausência de fill duplicado. [Resiliência I00](../evidence/I00-13-resiliencia.md) · [Livro-razão PAPER](../evidence/I03-persistencia-paper.md) |
| Filtros e precisão | P21/P32/P96/P106 · ADR-020/021/023/080 | Os ensaios PAPER demonstram validações locais de quantidade, nocional e colateral. Falta fonte versionada para o catálogo de filtros e regras por mercado, incluindo precisão e arredondamento, e testes de contrato com casos de limite e rejeição. [Custos PAPER](../evidence/I03-custos-paper.md) · [Futures PAPER](../evidence/I03-futures-paper.md) |
| Status e rastreabilidade | P22/P29/P31/P32 · ADR-021/027/028/052 | O fill PAPER preserva intenção, correlação e referência da cotação. Falta aprovar o mapeamento de estados, respostas desconhecidas e eventos fora de ordem, com contrato versionado e evidência de rastreio entre intenção, decisão, ordem e fill. [Market State em PAPER](../evidence/I03-market-state-paper.md) |
| Reconciliação e recuperação | P23/P29/P30/P31/P32/P82/P99/P106 · ADR-022/026–028/067/070/081 | I03 registra recomposição do estado a partir de fills e detecção de divergência. Falta demonstrar com fixtures externas sintéticas a comparação entre ordens, fills, saldos e posições, o bloqueio em divergência e a retomada após verificação de consistência e autoridade. [Livro-razão PAPER](../evidence/I03-persistencia-paper.md) · [Matriz I06](DOC-03-I06-TRACEABILITY.md) |

Para G3, Execution, QA e Risk precisam validar os critérios de TS-ST-022 e o escopo de P106, incluindo quais evidências de contrato e simulação podem ser aceitas e quais ainda exigem fonte adicional. O Evidence Bundle deve ligar candidato, versões, cenários, resultados, lacunas e decisão humana aos controles de IAM, Secrets, DR e OperationalReadiness de TS-ST-021. A inspeção não localizou relatório de homologação de TS-ST-022 no recorte consultado. Os testes acima foram conferidos por nome. Os resultados são históricos e sustentam apenas os recortes de dependência indicados.

## Validação de G3

O Blueprint associa G3 a IAM, DR, reconciliação, segredos e OperationalReadiness. Security, SRE e Risk são os responsáveis propostos. Ainda é preciso identificar o candidato, o ambiente de teste e as versões dos controles, confirmar os responsáveis e explicitar as dependências de I06 e TS-ST-022. Os testes devem usar identidades e segredos de teste em ambiente isolado.

P101 e ADR-087 orientam o Evidence Bundle. Ele deve reunir critérios aprovados, resultados de controle de acesso e segredos, medições de restore e reconciliação, testes de bloqueio e retomada, riscos residuais, hashes e vínculos aos gates anteriores aplicáveis. A revisão humana deve registrar escopo e decisão. G4 tem decisão própria.

A revisão foi documental. Os testes foram localizados por nome no checkout oficial. Os resultados citados pertencem a I00, I01 e I03. Não foi localizado dossiê de I07, execução integrada de OperationalReadiness ou decisão humana de G3 no recorte inspecionado. **G3 segue aberto e LIVE permanece indisponível.**
