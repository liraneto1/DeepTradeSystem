# Simulação Spot inicial em PAPER

O primeiro recorte de I03 exercita `TradingIntent → Control → Risk → Execution`
com BTCUSDT e cotação sintética. Use o terminal do VS Code na raiz do
checkout:

```powershell
uv sync --locked
uv run --no-sync pytest -v tests/unit/test_paper_simulator.py
```

1. **Control** exige PAPER, conta e ator autorizados, ausência de pausa
   e intenção dentro da validade.
2. **Risk** verifica a idade da cotação, quantidade, limite nocional,
   posição máxima, caixa e quantidade disponível para venda.
3. **Execution** aplica o fill e atualiza caixa e quantidade com
   decimais. O fill registra ID da intenção, ID de correlação e
   referência da cotação. Um reenvio idêntico dentro da validade
   devolve o mesmo fill sem novo efeito. Um ID repetido com conteúdo
   diferente é recusado.

Os limites e preços dos testes são valores sintéticos. Saldos e
deduplicação duram uma sessão em memória. O recorte executa uma compra
ou venda Spot integral pelo preço sintético. Persistência, reconciliação,
integração com Market State, Futures, taxas e slippage seguem em I03.
LIVE está indisponível e G0 segue aberto.

Na validação inicial passaram 14 casos da simulação e 101 testes na
suíte geral local. Os 22 testes que exigem PostgreSQL foram pulados
nesta execução. Ruff, formatação e mypy passaram.
