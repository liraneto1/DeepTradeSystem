# AC07 — Consolidação para revisão técnica

**16/11/2026 · Em revisão.** Base
`11e61c9a0875ed91ba68788063364f4dec44dfca` com alterações locais de
AC07 e AC09. A última suíte em PostgreSQL 17.11 descartável passou
com 152 testes, além de Ruff, formatação e mypy. O ensaio usou
PAPER, loopback, credenciais descartáveis e `LIVE_ENABLED=false`.
Nesta consolidação, os 16 SHA-256 do manifesto final foram
recalculados e coincidiram com o checkout oficial. A suíte citada
é a do ensaio anterior. [Manifesto de hashes](AC07-dispatcher-login-sha256.txt)

## Critérios demonstrados

| Critério | Resultado | Evidência |
|---|---|---|
| Conflito concorrente de versão | Um vencedor confirmou estado e evento. O concorrente sofreu rollback e o incidente permaneceu. Conta ausente participa da chave e outra conta pôde publicar. | [Conflito concorrente](AC07-conflito-concorrente-outbox.md) |
| Predecessor ausente, retido ou removido | Sucessores aguardaram sem tentativas. Foi demonstrada quarentena persistente, passagem de agregados independentes, escalonamento por idade e escalonamento imediato com comprovante de retenção. | [Quarentena](AC07-quarentena-retomada.md) · [Escalonamento](AC07-escalonamento-predecessor.md) |
| Reparo e efeito único | Após conflito contra versão já publicada, a liberação exigiu confirmar o consumo e restaurar a versão faltante. Versões 2 e 3 publicaram em ordem. Reenviar a versão 1 preservou o efeito único da projeção local. | [Reconciliação e retomada](AC07-quarentena-retomada.md) |
| Política e autoria | Limiar inicial de 3.600 s. Retenção mínima de 30 dias após publicação, com remoção manual de evento elegível. Retenção e retomada exigem papéis distintos e gravam a identidade PostgreSQL e a referência da decisão. | [Parâmetros](AC07-parametros-operacionais.md) · [Autorização](AC07-autorizacao-outbox.md) |
| Privilégio mínimo do dispatcher | Login dedicado autenticou e publicou. A CLI recusou login administrativo. APIs e SQL direto bloquearam a remoção e a liberação para o dispatcher. | [Login restrito](AC07-dispatcher-login-restrito.md) |

[Ensaio de referência anterior à correção](AC07-11e61c9-outbox.md)
· [DOC-04](../governance/DOC-04-OUTBOX-ORDERING.md)

## Pendências de aceite técnico

| Pendência | Evidência requerida e responsável funcional |
|---|---|
| Cardinalidade e fonte autoritativa | Engenharia e responsáveis pelos produtores confirmam um evento por versão para cada produtor que usar a Outbox e documentam a fonte de recuperação. O checkout atual contém a API e chamadas de teste. A confirmação operacional permanece aberta. |
| Mesmo ID com conteúdo divergente | Engenharia distingue replay equivalente de reuso divergente de `event_id`. A trilha persistente atual cobre a violação do índice de versão. QA demonstra que a colisão da chave primária com conteúdo divergente gera incidente durável, enquanto o replay equivalente preserva o efeito único. |
| Dados legados e remoções sem comprovante | Engenharia verifica se a base candidata contém colisões que inviabilizem o índice. Se houver colisões, QA valida a migração após reconciliação com decisão humana. Remoções sem comprovante são lacunas de origem desconhecida. A classificação como retenção exige evidência. |
| Controles dos operadores | Administração designa os logins individuais e valida as concessões no ambiente alvo. Engenharia e Segurança decidem se os grants SQL dos papéis de operação são aceitáveis com uso obrigatório das APIs ou se a elegibilidade e a auditoria devem ser impostas mesmo para SQL direto desses papéis. O ensaio de SQL direto cobre o login restrito do dispatcher. |
| Candidato e parecer | Engenharia identifica o commit candidato contendo as migrações `0016` a `0021` e vincula o ensaio, ou repete as verificações quando houver mudança. QA revisa cobertura, identidade e reprodução. O efeito único foi demonstrado na projeção do consumidor local. Consumidores operacionais exigem evidência própria quando integrados. |

O aceite técnico de AC07 permanece pendente de revisão humana.
LIVE permanece indisponível e G0 segue aberto.
