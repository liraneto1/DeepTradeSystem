# 04 — Segurança, aceite e evidências

## Política LIVE
LIVE não autorizado. I00 não deve possuir credenciais LIVE, endpoints de envio de ordens, adapters executáveis contra Binance real nem permissões de execução financeira. `LIVE_ENABLED=false` não substitui isolamento físico/lógico. Sem auto-resume para LIVE.

## Critérios de aceite I00
I00-AC01 build reproduzível; AC02 dependências controladas; AC03 contratos testados; AC04 migrations reproduzíveis; AC05 Outbox atômica; AC06 idempotência; AC07 ordenação por agregado; AC08 falhas e recuperação; AC09 observabilidade; AC10 segregação/LIVE inacessível; AC11 rastreabilidade; AC12 Evidence Bundle verificável.

## Cenários mínimos
Falha antes de commit → rollback total. Falha depois de commit → evento recuperável. Restart do dispatcher → continuidade. Duplicação → sem efeito duplo. Consumidor indisponível → retry/backlog. Evento fora de ordem → bloqueio/reordenação controlada. Contrato inválido → rejeição. Configuração de ambiente inválida → fail-closed.

## Gates
G0 Engineering Ready; G1 Strategy Validated; G2 PAPER Qualified; G3 Operationally Ready; G4 LIVE Limited; G5 LIVE Controlled. Nenhum gate foi homologado nesta documentação. Limites numéricos dependem de definição fundamentada e aprovação humana.

## Evidence Bundle
Identidade de release, commit, digest de build, ambiente, versões de contrato, resultados reais de testes, políticas, logs relevantes sanitizados, riscos, aprovação humana e hashes de integridade. Não inventar evidências ou status verde.
