# AC07 — Produtores, recuperação e pré-checagem de legado

16/11/2026. Checkout oficial com base
`11e61c9a0875ed91ba68788063364f4dec44dfca` e alterações locais de
AC07 e AC09. LIVE permanece indisponível e G0 segue aberto.

## Produtores e fonte de recuperação

A busca por `append_event`, `OUTBOX.insert` e INSERT na Outbox
encontrou a API transacional e chamadas em testes. Os resultados
de INSERT para auditoria, quarentena e tentativas são tabelas
auxiliares. O diagnóstico é um exemplo de contrato. O dispatcher
entrega eventos já gravados e a projeção local os consome.
Nenhum produtor operacional da Outbox foi identificado no
checkout. Os documentos de domínio condicionam eventos de Control,
Risk, Execution e Portfolio aos contratos de P31.

O [DOC-04](../governance/DOC-04-OUTBOX-ORDERING.md) e a migração
`0016` definem um evento por chave de ambiente, conta, tipo, ID
do agregado e versão. Conta ausente e nula ocupam o mesmo escopo.
A confirmação de que a regra atende cada produtor depende de seus
responsáveis. O [contrato](../03-CONTRATOS.md) estabelece versões
monotônicas e estado mais Outbox na mesma transação.
A [arquitetura](../01-ARQUITETURA-FISICA.md) define PostgreSQL como
fonte autoritativa do estado transacional. A origem recuperável
do envelope depende do produtor. O estado atual e o comprovante
de retenção, que contém o hash, podem corroborar o envelope.

Para cada produtor, registrar responsável, tipos de evento,
identidade do agregado, garantia de um evento por versão, origem
que preserva o envelope original e procedimento de recuperação.
A recuperação precisa preservar ID, versão e conteúdo e cruzar
o hash com o comprovante quando existir. Encaminhar casos sem
origem comprovada para revisão humana antes de retomar.

## Base legada e consulta

Não foi localizada instância PostgreSQL ativa ou exportação legada
no checkout oficial e nos diretórios locais de dados consultados.
Os dados reais continuam sem inspeção. Executar a consulta abaixo
contra um snapshot autorizado anterior à migração `0016`, em
PAPER ou TRAINING e com `LIVE_ENABLED=false`. Registrar a origem,
o ambiente, a data do snapshot e as quatro contagens.

```powershell
psql -X -v ON_ERROR_STOP=1 -f docs/evidence/AC07-consulta-colisoes-legadas.sql
```

A consulta usa uma transação somente leitura com Repeatable Read
e retorna apenas contagens. Ela replica a chave e a coerção
numérica do índice. Versões que impediriam a conversão recebem
contagem própria. Qualquer grupo em conflito ou erro de conversão
requer reconciliação e nova varredura antes da migração.

### Evidência executada

PostgreSQL 17.11 descartável, loopback, UTC, PAPER,
`LIVE_ENABLED=false`, credencial de teste e schema `0015`.
O fixture também incluiu uma linha TRAINING para testar escopo.

| Cenário | Linhas | Versões inválidas | Grupos em colisão | Linhas em colisão |
|---|---:|---:|---:|---:|
| Banco vazio | 0 | 0 | 0 | 0 |
| Fixture sintético | 5 | 0 | 1 | 2 |

A colisão usou IDs distintos, conta ausente ou nula e versões
numéricas 1 e 1.0. Outra conta, outro ambiente e a versão 2
ficaram fora desse grupo. `alembic upgrade 0016` rejeitou a
colisão sintética. A revisão permaneceu `0015`, e a segunda
varredura confirmou as cinco linhas e as mesmas contagens.
Nenhum dado real foi alterado.
