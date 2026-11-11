# Evidências do livro razão PAPER

Validação em 11/11/2026 com PostgreSQL 17.11 descartável. A suíte
passou com 126 testes, incluindo 25 de integração. Ruff, formatação e
mypy passaram. A migration `0008` foi aplicada e revertida na suíte.

| Cenário | Resultado |
|---|---|
| Replay após reinício | Dois processos Python devolveram o mesmo fill sintético. O banco manteve um fill e o caixa de 899,9987654322 após a compra de 0,01 BTC. |
| Reconciliação | A recomposição desde o saldo de abertura coincidiu com o caixa e a posição persistidos. Uma divergência induzida no teste foi detectada e vinculada à primeira intenção afetada. |
| Falha após inserir o fill | Uma restrição de teste bloqueou a atualização da conta. O rollback preservou o saldo de abertura e deixou zero fills. |
| Política LIVE | A abertura da conta foi bloqueada com configuração LIVE e nenhuma conta foi gravada. |

A chave de deduplicação é conta e ID da intenção. O teste de replay
usa o mesmo instante sintético, dentro da validade da intenção. A
simulação cobre Spot e usa preços sintéticos. G0 segue aberto.
[Guia de reprodução](../runbooks/paper-livro-razao.md)
