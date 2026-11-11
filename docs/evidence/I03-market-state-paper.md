# Evidências de Market State em PAPER

Validação em 11/11/2026 com PostgreSQL 17.11 descartável. Passaram
127 testes, incluindo 26 de integração. Ruff, formatação e mypy passaram.
A suíte aplicou e reverteu a migration `0009`.

| Cenário com relógio sintético | Resultado |
|---|---|
| Candle de 5m fica disponível depois da emissão, antes da execução | A intenção foi bloqueada e o saldo ficou intacto. |
| Fechamento solicitado após a emissão da intenção | A leitura foi recusada pelo corte temporal. |
| Estado completo com cotação vencida na execução | Risk recusou o fill. |
| Estado completo e cotação dentro da validade | O fill usou o fechamento de 5m. A transação gravou o estado estendido, suas 84 referências e o SHA-256. |
| Replay após recriar o livro-razão | Retornou o mesmo fill sem nova leitura. Alterar o fechamento com a mesma chave gerou conflito. |
| Evidência alterada ou removida | A reconciliação identificou a intenção divergente. |
| Intenção LIVE | Control bloqueou antes da leitura do estado. |

O ensaio cobre o caminho Spot com dados sintéticos e execução simulada.
LIVE permanece indisponível e G0 segue aberto.
[Guia de reprodução](../runbooks/paper-market-state.md)
