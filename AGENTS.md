# AGENTS.md — Instruções obrigatórias para agentes de engenharia

## Missão
Implementar incrementalmente o TRADE SYSTEM V1, respeitando a baseline `TS-ARCH-GLOBAL-V1.0` e a baseline técnica `TS-ENG-I00-V1.0`. Idioma da documentação e relatórios: português. Código e identificadores técnicos: inglês.

## Ordem de leitura
1. `docs/00-BASELINE-E-ESCOPO.md`
2. `docs/01-ARQUITETURA-FISICA.md`
3. `docs/02-I00-BACKLOG.md`
4. `docs/03-CONTRATOS.md`
5. `docs/04-SEGURANCA-E-ACEITE.md`
6. `docs/05-ADRS-TECNICAS.md`
7. `docs/06-PENDENCIAS-E-RASTREABILIDADE.md`
8. `docs/referencias/*.docx` quando necessário

## Regras inegociáveis
- **Nunca habilitar LIVE.** Não criar/usar credenciais LIVE, não enviar ordens reais, não habilitar endpoints de execução Binance, não permitir promoção automática. `LIVE_ENABLED=false` é proteção adicional, não suficiente: nenhuma capacidade de LIVE deve existir no I00.
- Não iniciar integração operacional Binance, PPO, UI ou ordens antes dos incrementos correspondentes.
- `TradingIntent -> Control -> Risk -> Execution` é obrigatório nos incrementos futuros; IA e UI nunca contornam Control/Risk.
- Preservar TRAINING/PAPER/LIVE segregados; I00 executa somente recursos locais de desenvolvimento/teste.
- Nunca inventar conteúdo integral das ADRs 001–088 ou descrições originais P01–P106. Marcar lacunas e pedir fontes.
- Nunca afirmar que gate G0–G5 foi aprovado sem evidências e decisão humana.
- Não modificar escopo aprovado ou escolher arquitetura conflitante sem registrar ADR de mudança e pedir aprovação.
- Não introduzir Kafka/Kubernetes/microsserviços desnecessários no I00.
- Usar tipos decimais exatos para dinheiro e quantidade; timestamps UTC; idempotência, correlação e versão nos contratos.
- Não colocar segredos em repositório, testes, logs ou exemplos.

## Protocolo de trabalho
1. Inspecionar repositório atual e `git status`; não sobrescrever trabalho do usuário.
2. Antes de editar, apresentar plano curto com arquivos, dependências, critérios de aceite e riscos.
3. Implementar **um work package por vez**, começando por I00-01, I00-02, I00-11.
4. Executar lint, tipos, testes e verificações disponíveis; registrar resultados reais, sem inventar passes.
5. Ao finalizar: listar arquivos alterados, comandos executados, evidências, pendências e próximos passos.
6. Não realizar push, deploy ou ações irreversíveis sem solicitação explícita.

## Definition of Done
Código revisável, configuração reproduzível, testes relevantes, rastreabilidade para work package/ADR, nenhuma exposição LIVE, documentação atualizada e evidência de execução.
