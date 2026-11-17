# Recuperação do RC1 e das fontes originais

Registro TS-DOC-GOV de 12/11/2026. O usuário aprovou nesta conversa o catálogo mínimo de I00 e a ordem de tratamento das lacunas. O aceite histórico de I00-14 e do bundle continua documentado na [revisão de 11/11](../evidence/revisao-g0-i00-rc1.md). A decisão de G0 segue em aberto.

## Bundle I00 RC1

O checkout de engenharia arquivado em `OneDrive/BUSINESS/06 - TRADE SYSTEM/03. ENGENHARIA/INTELIGENCIA ARTIFICIAL/DeepTradeSystem` forneceu o [SHA256SUMS](../evidence/releases/i00-rc1/SHA256SUMS) e os três artefatos em `dist/evidence/i00-rc1/`. Esse diretório é local e ignorado pelo Git. Os cinco arquivos de evidência já presentes no checkout conferiram com o checksum. Oito de oito hashes passaram na origem e no destino, incluindo ZIP, distribuição fonte e wheel. O comentário do ZIP contém o commit candidato completo `8d1467dd4087bcb6bb37fd4cc880de6d42b661e6`, também registrado no [manifesto](../evidence/releases/i00-rc1/manifest.json). O checkout atual não tem histórico Git para verificar o commit de publicação `3488ddd` localmente.

## Fontes originais

Foram copiadas 18 fontes para [originais](../referencias/originais/). O Blueprint e D01–D07 vieram de `02. ARQUITETURA` no mesmo acervo. O Engineering Foundation veio de `03. ENGENHARIA`. Cada um tem uma cópia Word e uma versão textual disponível no acervo. A versão textual é uma fonte complementar e pode incluir trechos diferentes do Word. O Blueprint mantém o nome original com `[Rascunho]`. Suas seções finais registram o encerramento e a aprovação de G01–G60. O Engineering Foundation registra a aprovação final de T01–T10 e TS-ADR-089–098.

Foi possível ler o XML interno dos nove Word. A conferência posterior vinculou P01–P106 aos sete arquivos textuais de domínio e à matriz de fases e localizou as decisões ADR-001–098. Os resultados e as ressalvas estão no [registro da reconciliação](RECONCILIATION-DECISIONS.md).

## O que ainda depende do usuário

| Item | Necessidade |
|---|---|
| Bundle, checksums, Blueprint, Engineering Foundation e D01–D07 | Recuperados. Nenhum reenvio necessário. |
| P18 | Mantido como M3 provisório conforme instrução de 12/11. A decisão definitiva segue em DOC-02. |
| ADRs individuais e atas | Se houver registros formais separados das fontes recuperadas, indicar a localização para complementar contexto, alternativas e consequências. |

Verificações executadas com PowerShell, `Get-FileHash`, leitura OOXML e busca de IDs com expressões regulares. O aceite desta etapa cobre recuperação e integridade dos arquivos de evidência. Os testes de software citados no bundle são históricos.

Em 16/11/2026, o usuário confirmou a retirada dos Word e adotou os [TXT atualizados](../referencias/originais/) como fontes oficiais. As menções anteriores a Word descrevem a recuperação histórica.

Em 16/11/2026, o usuário confirmou a retirada dos Word e adotou os [TXT atualizados](../referencias/originais/) como fontes oficiais. As menções anteriores a Word descrevem a recuperação histórica.
