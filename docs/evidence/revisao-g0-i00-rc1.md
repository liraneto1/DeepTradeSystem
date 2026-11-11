# Revisão de G0 com o candidato I00 RC1

Revisão em 11/11/2026. O usuário aprovou I00-14 e o Evidence Bundle
`i00-rc1`, referente ao commit candidato `8d1467dd4087bcb6bb37fd4cc880de6d42b661e6`
e publicado no commit `3488ddd`. Este registro documenta a aprovação do
bundle e a avaliação técnica de G0. A decisão humana sobre G0 segue pendente.
[Manifesto do candidato](releases/i00-rc1/manifest.json)

## Escopo do gate

D07, na seção “Gates de promoção aprovados”, exige para G0 implementação,
CI, testes, contratos e conformidade arquitetural, com Engenharia e QA
como responsáveis propostos. O Blueprint global, na Etapa 05, classifica
I00, I01 e I02 como G0 parcial e vincula I03 e I04 a G0. A decisão G49
mantém o aceite por incremento e os gates independentes. A evidência
disponível sustenta a contribuição de I00 ao gate. A recomendação é
manter G0 aberto até revisar as entregas e evidências de I01–I04.
[D07](../referencias/TS-ARCH-D07-V1.0.docx) · [Blueprint global](../referencias/TS-ARCH-GLOBAL-V1.0.docx)

A revisão usou as seções aprovadas dos documentos originais
`D07 — Engineering, Quality & Validation.docx` e
`[Rascunho] Architecture & MVP Blueprint.docx`, no acervo local.
Os links acima apontam para as reconstruções versionadas para consulta.

## Critérios de aceite de I00

Os oito hashes de `SHA256SUMS` conferiram, incluindo o snapshot, o wheel
e a distribuição fonte. O CI do commit candidato registrou 69 testes
gerais e 16 de integração em PostgreSQL 17 com sucesso.
[Checksums](releases/i00-rc1/SHA256SUMS) · [Execução do CI](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43086847472)

| Critério | Avaliação para o escopo I00 |
|---|---|
| AC01 · Build reproduzível | Evidenciado. Dois builds locais no mesmo ambiente produziram hashes idênticos. |
| AC02 · Dependências controladas | Evidenciado para lockfile e instalação com `--locked`. Avaliação de compatibilidade e segurança de release permanece em DOC-06. |
| AC03 · Contratos testados | Evidenciado para os envelopes v1 e os exemplos sintéticos. Testes de autorização, expiração e estado pertencem aos fluxos que aplicam essas regras. |
| AC04 · Migrations reproduzíveis | Evidenciado. Subida e reversão foram executadas em PostgreSQL 17 no CI. |
| AC05 · Outbox atômica | Evidenciado com estado sintético, commit e rollback. |
| AC06 · Idempotência | Evidenciado para o efeito gravado na mesma transação PostgreSQL, inclusive replay em outro processo. |
| AC07 · Ordem por agregado | Parcial. A versão posterior espera a anterior no fluxo da Outbox. Versões conflitantes e lacunas permanentes seguem em DOC-04. |
| AC08 · Falhas e recuperação | Evidenciado para as falhas exercitadas em I00-13, incluindo retry e reinício dos workers. A indisponibilidade foi simulada com uma porta local sem serviço. |
| AC09 · Observabilidade | Parcial. Diagnóstico, logs JSON e correlação foram validados. Métricas de backlog e atraso seguem em DOC-05. |
| AC10 · Segregação e LIVE indisponível | Evidenciado no ambiente local. TRAINING e PAPER têm segregação lógica e LIVE é rejeitado. |
| AC11 · Rastreabilidade | Evidenciado para os pacotes I00. A matriz global segue em DOC-01 a DOC-03. |
| AC12 · Evidence Bundle verificável | Evidenciado por manifesto, resultados e oito hashes conferidos. O usuário aprovou o bundle em 11/11/2026. |

[Critérios da baseline técnica](../04-SEGURANCA-E-ACEITE.md) · [Registro mestre de I00](../backlog/registro-mestre-i00.md)

## Pendências antes da decisão

- **Escopo de engenharia de G0.** Reunir implementação, contratos, CI,
  testes e evidência de conformidade de I01 (dados de mercado), I02
  (features e Market State), I03 (Control, Risk, execução simulada e
  Portfolio) e I04 (observações, PPO, registro e inferência). O candidato
  revisado cobre a fundação I00.
- **Cobertura parcial de I00.** Resolver ou registrar tratamento formal
  para DOC-04 e DOC-05. Consolidar a avaliação de dependências e o
  responsável pela revisão em DOC-06. A rastreabilidade global incompleta
  limita a verificação de conformidade dos incrementos seguintes.
- **Decisão de G0.** Engenharia e QA devem revisar evidências vinculadas
  ao candidato que cobrir o escopo aplicável e registrar a decisão humana
  correspondente. A aprovação de I00-14 encerra a revisão do bundle em
  DOC-07. A decisão de G0 em DOC-07 segue aberta.

Os critérios quantitativos aplicáveis serão revisados com seus respectivos
gates. G0 permanece aberto. LIVE permanece indisponível.
