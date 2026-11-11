# Evidências das features adicionais de I02

Validação em 11/11/2026 com PostgreSQL 17.11, usando os arquivos
verificados de I01 e I02 para o fechamento de 10/11/2025 às 22:35 UTC.
O estado estendido usa o schema `2.1.0` e as features `1.1.0`.
[Fórmulas e reprodução](../runbooks/market-state-btcusdt.md)

- **Spot e USDⓈ-M Futures:** comparei quatro features em cada um dos
  quatro intervalos com um cálculo separado sobre os candles lidos do
  PostgreSQL. Os 32 valores conferiram.
- **Linhagem:** cada intervalo apresentou 21 referências iguais às do
  estado `2.0.0` para o mesmo corte. O cálculo separado usou as aberturas
  registradas nessas referências para localizar os candles.
- **Corte temporal:** os dois mercados foram bloqueados quando o
  `as-of` antecedeu a disponibilidade do histórico.
- **Casos conhecidos:** momentum 0,25, RSI 100, amplitude relativa 0,08
  e fração compradora 0,75. Os testes também cobrem RSI 50 em janela
  plana, RSI 0 com perdas apenas e fração indefinida com volume zero.

Ruff, mypy e 109 testes locais passaram. A validação com dados reais
cobre um fechamento em cada mercado. A fração compradora usa o volume
agressor registrado nos candles. Profundidade de livro e dados
complementares de Futures seguem fora deste recorte.

LIVE permanece indisponível e G0 segue aberto.
