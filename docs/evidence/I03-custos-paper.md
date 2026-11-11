# Evidências de taxas e slippage em PAPER

Validação em 11/11/2026 com PostgreSQL 17.11 descartável. Passaram
129 testes, incluindo 28 de integração. Ruff, formatação e mypy passaram.
A suíte aplicou e reverteu a migration `0010`.

A conta sintética abriu com 1.000 USDT e zero BTC. A referência foi
10.000 USDT por BTC, com slippage de 100 bps e taxa de 10 bps.

| Fill de 0,01 BTC | Preço executado | Nocional | Taxa | Caixa após o fill |
|---|---:|---:|---:|---:|
| Compra | 10.100 | 101 | 0,101 | 898,899 |
| Venda | 9.900 | 99 | 0,099 | 997,800 |

A reconciliação confirmou caixa de 997,800 USDT e posição zero.
O replay em uma nova instância configurada com custo zero devolveu
o fill original. Alterar a taxa persistida no banco de teste fez a
reconciliação apontar a intenção divergente.

O Risk recusou a compra quando o nocional com slippage excedeu o
limite e quando o caixa cobria o nocional, mas ficava abaixo do custo
total. Nas duas rejeições, o saldo ficou intacto e nenhum fill foi
gravado. LIVE permanece indisponível e G0 segue aberto.
[Guia de reprodução](../runbooks/paper-taxas-e-slippage.md)
