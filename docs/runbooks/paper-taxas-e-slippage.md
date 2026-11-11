# Taxas e slippage em PAPER

O livro-razão persistente aceita uma política `ExecutionCosts` com
`fee_bps` e `slippage_bps`. Um ponto-base equivale a 0,01%. O padrão
é custo zero, inclusive para fills anteriores migrados pela revisão
`0010`. A política é sintética e explícita por sessão.

| Cálculo | Regra |
|---|---|
| Preço de compra | Referência × (1 + slippage em bps / 10.000). |
| Preço de venda | Referência × (1 − slippage em bps / 10.000). |
| Nocional | Preço executado × quantidade. |
| Taxa em USDT | Nocional × taxa em bps / 10.000. |
| Efeito no caixa | Compra debita nocional + taxa. Venda credita nocional − taxa. |

Risk aplica o limite por ordem ao nocional com slippage e verifica o
caixa da compra incluindo a taxa. O fill guarda o preço de referência,
o preço executado, a taxa e os dois valores em bps. A reconciliação
recalcula os custos com a política gravada em cada fill. Um replay
preserva o fill original mesmo se a política da nova sessão mudar.

Para reproduzir em PostgreSQL 17 descartável em `base`, siga a
[configuração PAPER](paper-livro-razao.md) e execute:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest -v tests/integration -k "paper_costed or paper_risk_uses"
Remove-Item Env:RUN_POSTGRES_TESTS
```

O downgrade para `0009` remove os campos de custo. Preserve os dados
de fills com custos antes de reverter a migration. LIVE permanece
indisponível e G0 segue aberto.
