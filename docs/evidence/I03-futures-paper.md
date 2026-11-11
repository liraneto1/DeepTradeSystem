# Evidências de USDⓈ-M Futures em PAPER

Validação em 11/11/2026 com PostgreSQL 17.11 descartável. A suíte passou
com 131 testes, incluindo 30 de integração. Um teste adicional verificou
o limite de posição vendida com quantidade decimal de alta precisão.
Ruff e mypy passaram. A migration `0011` foi aplicada e revertida.

Na conta sintética de 1.000 USDT, foram executados quatro fills de
0,01 BTC, com margem isolada a 1×, taxa de 10 bps e slippage de 100 bps.

| Fill | Preço executado | Margem após fill | P&L realizado no fill | Caixa após fill |
|---|---:|---:|---:|---:|
| Abertura long | 10.100 | 101 | 0 | 898,899 |
| Fechamento long | 10.890 | 0 | 7,9 | 1.007,6901 |
| Abertura short | 9.900 | 99 | 0 | 908,5911 |
| Fechamento short | 9.090 | 0 | 8,1 | 1.015,6002 |

A reconciliação confirmou posição e margem zeradas, P&L bruto de
16 USDT e caixa final de 1.015,6002 USDT. O replay em nova instância
preservou o fill original. Alterar a taxa persistida no banco de teste
fez a reconciliação identificar o fill divergente.

Os testes recusaram fechamento parcial, perda superior à margem
reservada, abertura sem colateral e intenção LIVE. Este recorte usa
cotações sintéticas. LIVE permanece indisponível e G0 segue aberto.
[Guia de reprodução](../runbooks/paper-futures.md)
