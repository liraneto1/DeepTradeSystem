# Verificação dos 20 critérios — candidato 0172728

Data 17/11/2026. SHA 0172728bd36c23247987a28c0fdccd32488e06f3. Resultado IN_REVIEW para parecer técnico e QA.

## Execuções

- Python 3.12.12 no ambiente local.
- Ruff aprovado; formatação de 96 arquivos aprovada; mypy sem problemas em 96 arquivos.
- Suíte completa com RUN_POSTGRES_TESTS=1: 153 passed in 75.82s.
- PostgreSQL 17 descartável, loopback 127.0.0.1, porta 58473, PAPER e LIVE_ENABLED=false. Instância encerrada ao final.
- Instalação em cópia limpa extraída do commit com uv sync --locked --offline aprovada.
- uv build --offline --no-sources aprovado; sdist e wheel produzidos.
- Contratos e imports na cópia limpa: 39 passed in 9.94s.
- Matriz adicional de compatibilidade: 12 casos aprovados, incluindo v1 válida e rejeição de versão desconhecida, campo extra, tipo alterado, valor fora do conjunto e campo obrigatório removido, por envelope.

## Recuperação do ambiente

A primeira tentativa encontrou ambiente virtual incompleto: mypy apresentou 137 erros e pytest falhou na coleta de 9 módulos por dependências ausentes. A sincronização offline pelo lockfile restaurou as dependências. A segunda execução completa passou. A instalação limpa foi executada separadamente para verificar reproduzibilidade do candidato.

## Resultado por critério

| Critério | Resultado | Evidência e pendência |
|---|---|---|
| ST001-AC01 | PARCIAL | Imports aprovados na cópia limpa; falta parecer de correspondência integral com a árvore e fronteiras da Feature. |
| ST001-AC02 | PASSOU no ambiente Windows | Instalação offline com lockfile e build de sdist e wheel aprovados em cópia limpa. |
| ST001-AC03 | PARCIAL | Qualidade, build e testes locais aprovados; falta execução de CI remoto no SHA e demonstração do bloqueio por falha. |
| ST001-AC04 | PENDENTE | Rastreabilidade documental disponível; responsáveis e pareceres técnico e QA ainda por designar. |
| ST002-AC01 | PASSOU | Exemplos de ambos os envelopes incluídos nos testes de contrato aprovados. |
| ST002-AC02 | PASSOU | Rejeições de campos, tipos, UTC, ambientes e versão cobertas pelos testes aprovados. |
| ST002-AC03 | APPROVED documental | Política inicial aprovada e presente no candidato. |
| ST002-AC04 | PASSOU no recorte v1 | 12 casos explícitos aprovados, seis por envelope, usando validação do consumidor v1. |
| ST002-AC05 | PARCIAL | P90/P61 delimitados documentalmente; falta relatório completo de contratos de domínio e seus responsáveis. |
| ST003-AC01 | PASSOU no recorte ensaiado | Suíte PostgreSQL inclui migrações round trip; revisar aplicabilidade do plano ao ambiente alvo. |
| ST003-AC02 | PASSOU | Commit conjunto de estado e Outbox coberto na suíte PostgreSQL. |
| ST003-AC03 | PASSOU | Rollback conjunto coberto na suíte PostgreSQL. |
| ST003-AC04 | PASSOU | Conflito concorrente e event_id divergente auditável cobertos pelos testes PostgreSQL aprovados. |
| ST003-AC05 | PARCIAL | Concorrência e constraints verificadas; cardinalidade por produtor, ownership operacional e legado ainda requerem confirmação. |
| ST004-AC01 | PASSOU no publisher local | Publicação, progresso e reinício cobertos pela suíte. |
| ST004-AC02 | PARCIAL | Efeito único e rollback do consumidor local testados; definir identidade de deduplicação para múltiplos consumidores lógicos. |
| ST004-AC03 | PASSOU no recorte local | Retry, falha retida, escalonamento e retenção cobertos; operadores alvo pendentes. |
| ST004-AC04 | PASSOU | Espera, progressão independente, chegada tardia e quarentena persistente cobertas na suíte. |
| ST004-AC05 | PARCIAL | Mecanismos de incidente e autorização testados; nomes/logins e fonte autoritativa por produtor pendentes. |
| ST004-AC06 | PARCIAL | Snapshot e transições aprovados no código atual; frequência e limiares operacionais ainda pendentes. |

## Limites e próximas decisões

A execução local verifica o recorte Windows e o publisher/consumidor de teste existentes. A execução de CI remoto vinculada ao SHA, o parecer de QA, os responsáveis nominais, a aplicação por produtores/consumidores operacionais e os parâmetros ainda abertos precisam de registro próprio. Os campos PASSOU indicam resultado no recorte descrito nesta matriz.

Os testes foram executados no checkout BUSINESS com código correspondente ao candidato; instalação, build, imports e contratos também foram verificados em extração limpa do SHA. Os logs foram preservados junto a este relatório. A integridade Git do código e os manifestos foram conferidos ao final.
