# Market State na execução simulada em PAPER

`submit_market_intent` integra o Market State de BTCUSDT ao fluxo
`TradingIntent → Control → Risk → Execution`. O recorte usa Spot e o
Market State estendido de quatro intervalos. O preço do fill simulado
é o último fechamento de 5m do estado.

| Horário | Uso |
|---|---|
| `close_at` | Fecha a janela de decisão de 5m e alinha os outros intervalos. |
| `intent.issued_at` | Limita quais candles já estavam disponíveis quando a intenção foi emitida. |
| `now` | Verifica a validade da intenção e a idade da cotação na execução simulada. |

Control autoriza a intenção antes da consulta. O Market State precisa
estar completo nos quatro intervalos. Risk aplica seus limites e pode
rejeitar uma cotação vencida mesmo quando o estado existe. A migration
`0009` grava o estado completo com o fill, cujo `quote_reference`
identifica o SHA-256 do JSON canônico. A reconciliação confere o hash.

Um replay com a mesma intenção e o mesmo fechamento, dentro da
validade, devolve o fill gravado e dispensa nova leitura de mercado.
Alterar o fechamento com a mesma chave de idempotência é conflito.
A reversão para `0008` remove os estados anexados aos fills.

Para reproduzir o teste em um PostgreSQL 17 descartável em `base`,
use a [configuração PAPER](paper-livro-razao.md) e execute:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run --no-sync pytest -v tests/integration -k paper_market_state
Remove-Item Env:RUN_POSTGRES_TESTS
```

O teste usa candles sintéticos com horários de disponibilidade
controlados. LIVE permanece indisponível e G0 segue aberto.
