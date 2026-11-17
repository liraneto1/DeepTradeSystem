# Decisões pendentes da reconciliação

Registro de 12/11/2026 em `IN_REVIEW`. Foram reconciliados 106 IDs de pendências com seus registros de domínio e a fase primária da Etapa 04, além de 98 decisões de ADR com seus registros de aprovação. A cobertura é documental. Vínculos individuais com componentes, histórias, testes e evidências seguem em DOC-03. Nenhuma fase foi reclassificada.

- [Pendências por ID e fase](PENDING-ITEM-RECONCILIATION.md)
- [ADRs por ID e registro de aprovação](ADR-RECONCILIATION.md)
- [Blueprint e fontes de domínio](../referencias/originais/)

## Decisões que permanecem abertas

| Item | Divergência ou lacuna | Tratamento atual | Decisão ou evidência necessária |
|---|---|---|---|
| P18 · DOC-02 | D02, linhas 360 e 505, reúne detecção de degradação e gatilhos de retreinamento. A Etapa 04, na matriz e nas ressalvas da Etapa 04, preserva M3 provisório. | M3 provisório, conforme instrução de 12/11. | No fechamento de DOC-02, registrar decisão G40 sobre a fase e sobre eventual separação entre detecção e retreinamento. |
| P45 e P47 · D04 | A matriz global mantém M2. D04 inclui segregação por ambiente em P45 e reúne testes E2E, acessibilidade, segurança e falhas em P47. G40 prevê antecipação de segurança crítica para PAPER. | M2 para as pendências integrais. Os controles e testes de segurança já aprovados para I00 continuam exigidos no seu próprio recorte. | Antes do aceite do escopo PAPER da interface, aprovar quais partes de P45 e P47 são críticas e onde serão verificadas. Qualquer mudança da fase primária requer G40. |
| P53 · D05 | D05, linhas 558 e 817, recomenda resolver inicialmente o modelo de armazenamento histórico e particionamento. A matriz global, Etapa 04, matriz de priorização, registra M2. | M2. Preservada a recomendação de domínio como contexto de planejamento. | Se o particionamento ou o modelo definitivo for dependência de um incremento anterior, registrar a dependência com evidência e submeter a antecipação a G40. |
| P08, P17, P29–P32, P59, P62, P65, P70, P82, P97 e P100 | As ressalvas da Etapa 04, na seção “Observações sobre itens críticos”, distinguem mínimos para PAPER de reforços, critérios formais e condições de promoção. As tabelas de domínio registram o escopo agregado. | Mantidas as fases primárias por ID. I00 segue o recorte local e os critérios aprovados em sua baseline. | Durante o refinamento, registrar para cada recorte crítico a história, critério, teste e responsável. Submeter a decisão humana quando houver mudança de escopo, fase ou critério de aceite. |
| ADRs formais | As fontes contêm tabelas de aprovação e, em vários casos, formulações anteriores. A ficha de TS-ADR-093 documenta contexto, alternativas e consequências e conserva o estado histórico `PROPOSED`. A tabela final aprova a decisão. | As 98 decisões têm referência. A ficha de 093 e sua aprovação posterior estão vinculadas no índice. | Indicar atas ou fichas individuais versionadas, se existirem. Para formalizar itens sem registro completo, fornecer a origem de contexto, alternativas e consequências ou aprovar um registro retrospectivo que explicite os campos sem fonte. |
| DOC-03 e DOC-06 | Os domínios indicam áreas funcionais. A origem recuperada não estabelece responsáveis nominais nem todos os vínculos por pendência. | Áreas de origem preservadas. Vínculos ainda sem evidência ficam abertos. | Indicar responsáveis e fornecer eventual registro mestre aprovado ou decisões de vínculo. Usar as histórias e os critérios existentes para completar os vínculos demonstráveis no refinamento. |

## Diferenças resolvidas pela leitura conjunta

- P15 está em M0 para o **contrato** do Research Agent. ADR-008 e o Blueprint, linha 1455, deixam a implementação completa para depois. Mantida a distinção entre contrato e implementação.
- A correção aritmética do Blueprint, linha 1826, confirma **68 / 28 / 9 / 1**. A contagem foi reproduzida a partir dos 106 IDs da matriz. As fases individuais permanecem como registradas.
- As variantes resumidas das pendências omitem detalhes em alguns casos, por exemplo limitações do simulador em P12, ordenação em P42, consulta em P44 e observabilidade em P64. A tabela preserva a redação original e a variante para revisão, sem interpretar o resumo como retirada de escopo.
- Em TS-ADR-089–098, as propostas anteriores são históricas. A seção de aprovação final do Engineering Foundation, linhas 824–855, é a referência de decisão. Inclui Hypothesis em TS-ADR-094 e registra LIVE indisponível em I00 em TS-ADR-098.

DOC-01 tem a etapa de confronto documental coberta para P01–P47, com ressalvas acima. DOC-02 permanece aberto com M3 provisório. DOC-03 tem um [recorte inicial para I00](DOC-03-I00-TRACEABILITY.md), com lacunas por pendência e distinção entre o snapshot do RC1 e o checkout atual. A decisão humana de G0 continua pendente.
