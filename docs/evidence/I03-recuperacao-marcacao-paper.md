# I03 — Recuperação do histórico de marcação em PAPER

A migração `0015` persiste OHLC de BTCUSDT USDⓈ-M em candles de
marcação de 1 minuto. O coletor fixa o fim da janela no início
do minuto corrente e exige páginas completas antes de gravar.
O recebimento local define a disponibilidade. A leitura temporal
filtra o fechamento e a disponibilidade pelo corte correspondente.

O coletor retoma da primeira lacuna no intervalo configurado.
Reprocessar uma janela preserva a primeira disponibilidade. A
restrição por abertura impede duplicatas, e dados conflitantes
em gravações sobrepostas são rejeitados. A recuperação de OHLC
permite auditar a interrupção. A liquidação continua avaliando
a marcação atual, sem simular a sequência intraminuto.
[Guia PAPER Futures](../runbooks/paper-futures.md)

## Evidências

- Ruff e mypy passaram em 84 arquivos.
- `RUN_POSTGRES_TESTS=1` com `python -m pytest -q` em PostgreSQL 17
  descartável passou com 143 testes.
- A integração interrompeu a segunda página, recriou a conexão
  e recuperou só o minuto faltante. Confirmou duas linhas após
  reprocessamento e ocultou candles antes do recebimento ou fora
  da janela consultada.
- A API pública retornou três candles fechados na janela de teste.
- A CLI expôs a opção `--recover-from`. A migração foi testada
  nos dois sentidos.

O [CI de I01](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43095464339)
do commit `e8f7b51` seguia na fila na consulta desta entrega.
LIVE permanece indisponível e G0 segue aberto.
