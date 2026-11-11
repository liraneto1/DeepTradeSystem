# Evidence Bundle I00 RC1

O candidato `i00-rc1` consolida a fundação técnica de I00 para revisão.
O [manifesto](manifest.json) identifica o commit candidato, as baselines,
as versões de contratos e migrations, a configuração sanitizada, os
artefatos e as decisões humanas. O commit que publica este dossiê é
posterior ao commit candidato.

- [Resultados de testes e build](test-results.json)
- [Amostra sanitizada de log](diagnostic-log.json)
- [Checksums SHA-256](SHA256SUMS)
- [Registro mestre e critérios de aceite](../../../backlog/registro-mestre-i00.md)

## Como verificar os arquivos no VS Code

Os artefatos foram gerados no checkout principal em
`dist/evidence/i00-rc1/`. O ZIP representa os arquivos versionados do
commit candidato. O wheel e a distribuição fonte foram gerados com uv.
Os dois builds locais, com o mesmo snapshot, ferramentas e
`SOURCE_DATE_EPOCH`, produziram os mesmos hashes. Os hashes de build
se referem a esses artefatos locais. O GitHub Actions fornece evidência
independente de execução dos testes e do build.

O ZIP contém o checkout completo para executar os processos. O wheel
empacota os módulos de `trade_system`. Os três arquivos de build ficam
em `dist/`, que é ignorado pelo Git.

Na raiz do repositório, execute no terminal PowerShell:

```powershell
Get-Content docs/evidence/releases/i00-rc1/SHA256SUMS | ForEach-Object {
    $expected, $file = $_ -split '  ', 2
    $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
    if ($actual -ne $expected) { throw "SHA-256 divergente em $file" }
    Write-Output "OK $file"
}
```

## Pendências para revisão

| Referência | O que ainda precisa de decisão ou evidência |
|---|---|
| DOC-01 a DOC-03 | Reconciliar P01–P47, confirmar P18 e completar a rastreabilidade global com as fontes originais. |
| DOC-04 | Definir reconciliação de versões conflitantes e lacunas permanentes de eventos. I00-13 verificou a espera pela versão anterior quando ela chega depois. |
| DOC-05 | Medir backlog e atraso da Outbox e registrar evidências das métricas. |
| DOC-06 | Avaliar compatibilidade e segurança das dependências de release e definir responsáveis, capacidade e decisões de produção. |
| DOC-07 | Revisar este bundle e registrar a decisão humana sobre I00 e G0. Critérios quantitativos e os demais gates seguem pendentes. |

As aprovações de pacotes registradas na conversa dizem respeito ao
desenvolvimento de I00. O aceite do bundle e o gate G0 aguardam decisão
humana. LIVE permanece indisponível.
