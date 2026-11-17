# Posição atual do projeto e escopo ativo

17/11/2026. Referência: fluxo de revisão desta conversa e candidato ac51f91cfc08dadae3a3bb411908b0b9a26f11af, no DeepTradeSystem do BUSINESS.

## Fase atual

Consolidação e aceite técnico da fundação I00 — Engineering Foundation, no recorte das quatro primeiras histórias formais. A atividade atual trata de I00-AC02: controle, compatibilidade e segurança das dependências.

| História | Recorte aprovado | Posição observada |
|---|---|---|
| TS-ST-001 | Estrutura modular, toolchain, build, CI e rastreabilidade | Ficha e critérios aprovados; candidato e CI remoto verificados. Segurança de dependências e pareceres nominais pendentes. |
| TS-ST-002 | CommandEnvelope/EventEnvelope 1.0.0 e compatibilidade | Ficha, política e recorte aprovados; testes e relatório de cobertura disponíveis. Aceite técnico humano e responsáveis pendentes. |
| TS-ST-003 | PostgreSQL, migrations e atomicidade estado/Outbox no produtor sintético | Ficha e recorte aprovados; testes transacionais, concorrência e recuperação executados. Revisão final técnica/QA pendente. |
| TS-ST-004 | Publisher PostgreSQL local, consumidor diagnóstico, idempotência, retomada e monitor | Ficha, parâmetros, implementação do monitor e resultados aprovados; suíte e CI executados. Operadores, conta/serviço, supervisão e canal externo de alertas pendentes. |

Os 20 critérios foram aprovados como especificação de verificação. Essa aprovação documental e as execuções de testes ainda exigem o fechamento das pendências e a decisão de aceite da entrega.

## O que já foi demonstrado neste fluxo

- Recuperação de fontes e proveniência, fichas e vínculos tratados e aprovados conforme as decisões da conversa.
- Candidato anterior 0172728 revisado, com decisões de escopo e cobertura técnica documentadas.
- Monitor local de TS-ST-004 implementado e aprovado pelo usuário.
- Candidato ac51f91 publicado na branch de revisão; CI remoto do candidato passou com 115 testes unitários/contratos e 49 integrações PostgreSQL.
- Bloqueio por falha obrigatória demonstrado em branch temporária, posteriormente removida por autorização.
- Inventários de build e bibliotecas, SBOM, triagem de backports, avaliação da imagem PostgreSQL/gosu e alternativas de cliente em teste, com riscos registrados.

## O que falta para esse aceite técnico

1. Revisar a alternativa de cliente e decidir sobre a ausência de LDAP/GSSAPI no recorte I00, antes de alterar o candidato.
2. Registrar a decisão de segurança para os riscos residuais do cliente, ferramentas de build e imagem PostgreSQL/gosu.
3. Definir responsáveis técnicos, QA e operadores individuais; obter os pareceres correspondentes.
4. Definir ambiente, conta de serviço, supervisão do monitor e destino/destinatários dos alertas.
5. Se houver mudança aprovada: produzir novo candidato, repetir as verificações aplicáveis e registrar a decisão humana de aceite das quatro histórias.

## Relação com o projeto completo

A baseline abrange I00–I09. Este fluxo está fechando um recorte de I00; não há percentual global confiável de conclusão do TRADE SYSTEM V1 a derivar dessas quatro histórias.

O checkout contém código e evidências históricas de outros recortes, inclusive simulações. O estado formal de cada incremento deve ser lido nas suas próprias evidências e decisões de aceite.

G0 permanece aberto conforme os registros consultados; esta atividade não o avaliou nem homologou. PAPER Qualified e LIVE permanecem sem homologação. LIVE segue desabilitado.

Próximo marco deste fluxo: encerrar as pendências de segurança e responsabilidades, consolidar um candidato revisado quando autorizado e obter o aceite técnico das quatro histórias.

## Fontes

docs/00-BASELINE-E-ESCOPO.md; docs/02-I00-BACKLOG.md; docs/04-SEGURANCA-E-ACEITE.md; docs/backlog/TS-ST-001.md a TS-ST-004.md; docs/evidence/ci-ac51f91/RESULTADOS.md; docs/evidence/ci-ac51f91-audit/RESULTADOS.md; docs/evidence/ts-st-004-monitor/RESULTADOS.md; aprovações explícitas desta conversa.

O registro mestre de I00 e a matriz inicial dos 20 critérios conservam retratos históricos. A síntese acima considera também as execuções e decisões posteriores identificadas pelas evidências, sem reescrever as baselines ou atribuir aprovação implícita de gates.
