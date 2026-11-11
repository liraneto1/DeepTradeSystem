# Consolidação de I02

O usuário aprovou as três etapas de I02 até as features adicionais em
11/11/2026. A validação usou dados públicos de BTCUSDT em Spot e USDⓈ-M
Futures e PostgreSQL 17 local.

| Entrega | Evidência |
|---|---|
| Estado de 5m | 21 candles consecutivos e bloqueio antes da disponibilidade do arquivo. [Recorte inicial](I02-market-state-inicial.md) |
| Estado de 1m, 5m, 15m e 1h | Alinhamento com o fechamento de decisão e 84 referências de origem por estado. [Contexto multi-intervalo](I02-market-state-multi-intervalo.md) |
| Features adicionais | 32 valores recalculados a partir dos candles da linhagem. Momentum, RSI simples, amplitude relativa e fração compradora agressora. [Cálculos e rastreabilidade](I02-features-adicionais.md) |

A [execução da ingestão contínua de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
permaneceu na fila na verificação de 11/11/2026. As verificações locais
constam na [consolidação de I01](I01-consolidacao.md).

A amostra cobre fechamentos específicos e mantém o corte de
disponibilidade. Livro de ofertas, dados complementares de Futures e
validação quantitativa permanecem pendentes. LIVE está indisponível e
G0 segue aberto.
