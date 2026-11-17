# AC02 — Avaliação de cliente Psycopg/libpq com bibliotecas mantidas

17/11/2026. Estado IN_REVIEW. Projeto: DeepTradeSystem do BUSINESS.
Candidato preservado: ac51f91cfc08dadae3a3bb411908b0b9a26f11af.

## Parecer para revisão

Recomendo o perfil experimental Linux/amd64 Alpine 3.24 com Psycopg C 3.3.8 e libpq 18.7 para o recorte I00 de autenticação por senha/TLS, condicionado à aprovação de compatibilidade: esse libpq é compilado sem LDAP/GSSAPI. As bibliotecas antigas embutidas no psycopg-binary deixam de acompanhar o runtime. Não se trata de substituição funcional irrestrita.

O ensaio final passou em 164 testes, qualidade, tipos, build e três casos de TLS. Trivy 0.76.2 retornou zero ocorrências no runtime mínimo identificado abaixo. As duas extensões C e outros 37 arquivos nativos comuns entre teste e runtime têm hashes idênticos.

AC02 permanece em revisão: faltam decisão sobre o perfil, disposição de segurança dos riscos residuais, responsáveis/QA e um futuro candidato com as mudanças aprovadas. Não houve alteração de código, pyproject, lockfile, imagem configurada ou baselines do candidato.

[Estado atual do escopo](ESTADO-DO-ESCOPO.md) · [Proposta concreta de adoção](PROPOSTA-ADOCAO.md).

## Comparação executada

| Alternativa | Configuração efetivamente observada | Funcional | Scanner do runtime | Conclusão |
|---|---|---|---|---|
| Debian 13 | Python 3.12.16; Psycopg C 3.3.8; libpq 17.12; krb5 1.21.3-5+deb13u1; OpenLDAP 2.6.10+dfsg-1 | 164 testes, qualidade/build e TLS passaram | 316 ocorrências, 129 CVEs únicos: 103 HIGH, 119 MEDIUM, 89 LOW, 5 UNKNOWN; zero CRITICAL | Corrige GSS antigos, mas conserva avisos de pacote e uma linha LDAP anterior a correções cliente. Não recomendo adotá-la como está. |
| Alpine, primeiro runtime com instalador | Python 3.12.16; Psycopg C 3.3.8; libpq 18.7-r0; OpenSSL 3.5.9-r0 | 164 testes e TLS passaram | 6 ocorrências de pip 25.0.1: 5 MEDIUM, 1 LOW; zero em pacotes das bibliotecas carregadas | O instalador herdado precisava de tratamento. |
| Alpine com pip 26.3 | Mesmo cliente; wheel de build atualizado para 0.48.0 | 164 testes e TLS passaram | 3 ocorrências no setuptools 70.3.0 embutido no instalador: 1 HIGH, 1 MEDIUM, 1 LOW | Atualizar o instalador manteve componentes vulneráveis embutidos; esta variante não é a recomendada. |
| Alpine mínimo, final | Mesmo cliente; compilação separada; sem pip e sem wheels de bootstrap ensurepip no runtime | 164 testes, qualidade/build, TLS e identidade nativa passaram | Zero ocorrências retornadas | Preferido para o recorte delimitado, sujeito à decisão de compatibilidade e revisão humana. |

As contagens são ocorrências pacote/CVE de imagens cliente, não uma comparação direta com as antigas contagens da imagem servidor PostgreSQL. Em Debian, 129 ocorrências atingem pacotes que possuem bibliotecas carregadas, inclusive 56 HIGH; a classificação por pacote não demonstra que o código vulnerável esteja no caminho cliente. Diversos avisos são de KDC/kadmind/RPC e exigem disposição por escopo.

Os testes repetem a mesma suíte; não representam centenas de requisitos independentes adicionais. O primeiro ensaio Debian comparou builds C separados na suíte e no runtime. A conferência detectou diferença de hashes nas duas extensões; na alternativa Alpine adotamos o mesmo wheel C nos dois ambientes e passamos a verificar igualdade explícita antes dos testes.

## Identidade do ensaio final

- [Execução final](https://github.com/liraneto1/DeepTradeSystem/actions/runs/44150219172), workflow 4f9103cbe2a8eb255dcc453e54e9882102508905, branch review/ac02-maintained-client-alpine-ac51f91.
- Código extraído de ac51f91; somente a cópia temporária de dependências e o ambiente de teste recebem a variação.
- Base por digest: python@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89.
- Runtime executado e auditado: sha256:3aafad3cefe17646cdeb35b795f594525375f87db1ad3066be9aa385d9ae1673.
- Psycopg 3.3.8, implementação c; libpq de build e execução: 180007, isto é, 18.7.
- APKs: libpq 18.7-r0, libcrypto3/libssl3 3.5.9-r0, musl 1.2.6-r3; krb5-libs instalado na imagem 1.22.3-r0, sem compor o caminho GSS do cliente.
- Fonte libpq vinculada ao commit aports 33a57d3919ee0227231f5a3e599540514584e309; origem, versões e commits dos APKs em VERIFICATION.json e no inventário instalado.
- Artefato 14359485631. ZIP SHA256 b8dc948e96b1e22e88d7c9ee5febe144323f7bafd9f3ea8b5bc910304d6159cb.
- 116 arquivos do manifesto remoto verificados diretamente no ZIP: zero divergências. A verificação direta também cobre arquivos com caminhos longos no Windows.
- Scanner e base de vulnerabilidades estão identificados nos JSON e digests preservados; não houve filtro por severidade ou ignore de CVE para obter o resultado zero.

## Verificações executadas

| Verificação | Evidência / resultado |
|---|---|
| Candidato intacto | HEAD local ac51f91; hashes de pyproject.toml e uv.lock antes/depois do ensaio iguais; nenhuma diferença nos arquivos de implementação do candidato. |
| Dependências Python | Nenhuma versão comum foi alterada. psycopg-binary removido da cópia; psycopg-c 3.3.8 acrescentado. Ferramentas de build registradas separadamente. |
| Fonte C | Sdist oficial PyPI com hash validado, preservado, compilado contra headers libpq do sistema; wheel resultante preservado. |
| Fechamento de dependências | uv pip check aprovado no ambiente de teste e no venv mínimo. |
| Qualidade | Ruff, formatação e mypy aprovados; mypy examinou 98 arquivos. |
| Build | Wheel C e sdist/wheel do projeto construídos com logs preservados. Build do projeto sem isolamento usa ferramentas inventariadas. A instalação inicial locked tem seu próprio log. |
| Suíte | JUnit: 164 testes, zero falhas, zero erros, zero skips; 28,20 s no ensaio final. Inclui 49 integrações PostgreSQL e 115 testes unitários/contratos. |
| Identidade dos binários | 39 arquivos comuns, incluindo _psycopg e pq, com hashes iguais; zero diferenças. IDs de imagens conferem com os usados na execução. |
| TLS positivo | Conexão SQL com verify-full e certificado de teste confiável; TLS 1.3, TLS_AES_256_GCM_SHA384. |
| TLS negativo | Nome de servidor incorreto e raiz de confiança ausente foram rejeitados. São casos específicos; não equivalem à cobertura exaustiva de TLS/autenticação. |
| Inventário / scanner | SBOM CycloneDX, pacotes APK, origem/commit e bibliotecas carregadas preservados; zero ocorrências no runtime final. |

Servidor de teste PostgreSQL 17.12, dados descartáveis, loopback, PAPER e LIVE_ENABLED=false. O digest do servidor foi postgres@sha256:a77aa70e641402a21411b92b721c58d10f23b50ae5fdd2333efd22d166e1e5f7. A escolha do cliente não incorpora automaticamente a imagem gosu recompilada do ensaio anterior. O tratamento e aceite da imagem servidor continuam separados.

## Achados anteriores e procedência

| Achado anterior | Tratamento observado no perfil recomendado |
|---|---|
| CVE-2024-37370/37371 no bundle Kerberos antigo | O cliente não oferece GSSAPI; não carrega aquelas bibliotecas antigas. O krb5 instalado no sistema é 1.22.3-r0, com secfixes do fornecedor registrados. Em Debian, a linha 1.21.3-5+deb13u1 também é declarada corrigida pelo fornecedor para esses dois CVEs. |
| PCRE 8.32, SELinux, SASL e dependências antigas do wheel | O diretório psycopg_binary.libs foi removido na cópia. A cadeia efetivamente carregada usa bibliotecas do Alpine. Não é correto herdar automaticamente os CVEs do pacote antigo para componentes novos ou ausentes. |
| libldap/liblber de versão/procedência incompletas | Não são instaladas nem carregadas no runtime proposto, por opção de compilação do fornecedor. Isso elimina sua distribuição nesse perfil, sem resolver retroativamente a lacuna do wheel histórico. |
| libcrypt desconhecida do wheel | Não há libcrypt.so externa no runtime proposto; a lacuna histórica permanece identificada para o artefato anterior. |
| Ferramenta wheel antiga introduzida no primeiro ensaio | Atualizada de 0.45.1 para 0.48.0. O aviso CVE-2026-24049 não é retornado para essa versão na consulta OSV. |
| pip/instaladores herdados | Removidos do runtime, incluindo os wheels de bootstrap de ensurepip. Atualizações passam a exigir reconstrução da imagem, não instalação dinâmica no runtime. |

Fontes: [instalação local Psycopg](https://www.psycopg.org/psycopg3/docs/basic/install.html), [API de identificação da implementação/libpq](https://www.psycopg.org/psycopg3/docs/api/pq.html), [CVE-2024-37370 Debian](https://security-tracker.debian.org/tracker/CVE-2024-37370), [CVE-2024-37371 Debian](https://security-tracker.debian.org/tracker/CVE-2024-37371), [secdb Alpine 3.24](https://secdb.alpinelinux.org/v3.24/main.json).

## Diferença funcional que depende de decisão

A receita Alpine do libpq 18.7 constrói as interfaces sem LDAP. O binário oficial contém as mensagens de GSSAPI não compilado e autenticação GSSAPI não suportada. O APK foi baixado da origem oficial e o SHA256 do ELF comparado ao arquivo carregado no runtime final: coincidência integral. Ver libpq-apk-capabilities.json e alpine-libpq-APKBUILD.txt.

O perfil atende aos testes atuais de banco local com senha/TLS. LDAP, GSSAPI/Kerberos e SSPI não fazem parte da capacidade proposta. Se forem requisitos, deve-se escolher outra configuração mantida e verificá-la antes de substituição. Não houve remoção dessas capacidades no candidato vigente.

## Riscos residuais e limites do parecer

1. **Compatibilidade:** Linux/amd64 com musl foi ensaiado. Windows, ARM e Linux glibc exigem sua própria verificação. A proposta conserva uma via Windows e requer testá-la no futuro candidato.
2. **Ferramenta de build:** o sdist Psycopg C 3.3.8 exige setuptools 83.0.0. A OSV retorna GHSA-xmj3-9gf7-h52w para essa versão; o aviso descreve caminho legado de instalação de wheel específico de Windows. O build foi Linux, e a ferramenta não está no runtime. Proposta de não aplicabilidade nesse recorte, ainda sem aprovação de Segurança. Não alteramos silenciosamente a exigência upstream.
3. **Cobertura do scanner:** zero ocorrências na base consultada não prova ausência de vulnerabilidades, código inalcançável ou cobertura completa de CPython, compilador e cadeia de build. O inventário/OSV das ferramentas Python não constitui auditoria integral do sistema de compilação.
4. **Manutenção:** é necessário definir owner e rotina de reconstrução/revalidação de APKs, base, Python e wheel C. Fontes e base foram fixadas por identidade; o teste usou repositórios correntes. A versão futura do candidato deve controlar também a resolução dos APKs e a retenção dos artefatos.
5. **Atestação:** existem hashes, receitas, metadados de pacotes e logs de build. Não foi emitida atestação assinada própria do novo wheel C.
6. **Distribuição:** a imagem experimental não foi publicada ou preservada como tar de imagem; o wheel C, o sdist e a receita foram preservados. A adoção exige novo build/candidato e repetição dos controles aplicáveis. Não promover apenas pelo ID efêmero do teste.
7. **Uso operacional:** não houve carga representativa, teste de autenticação corporativa, failover produtivo ou homologação de PAPER/LIVE. A evidência está limitada à suíte e aos três casos TLS descritos.
8. **Servidor e aceite:** imagem PostgreSQL/gosu, riscos de build e pareceres técnico/QA continuam sujeitos a decisões específicas. Nenhum gate foi avaliado ou aprovado.

Os avisos de build e instaladores estão em python-osv*.json e nos JSON individuais. A consulta preservada contém os pacotes reais do inventário e uma verificação das versões corrigidas de wheel/pip; o resultado remanescente é o aviso Windows de setuptools 83.0.0. Esse aviso não foi tratado como correção instalada nem suprimido silenciosamente.

## Artefatos e reprodução

- RESULTADOS.md e PROPOSTA-ADOCAO.md: parecer e mudança proposta, sem adoção.
- ESTADO-DO-ESCOPO.md: posição do projeto e próximos marcos.
- SUMMARY.json e VERIFICATION.json: contagens, deltas e verificações de identidade.
- DEBIAN-FINDINGS.csv, ALPINE-FINDINGS.csv, ALPINE-FINAL-FINDINGS.csv, ALPINE-RUNTIME-FINDINGS.csv: cada etapa separada; a última possui apenas o cabeçalho, pois não há ocorrências.
- PRIOR-FINDINGS-COMPARISON.csv: comparação de 215 relações anteriores com estados do fornecedor Debian; NOT_LISTED não significa seguro.
- alpine-runtime/audit: logs, JUnit, SBOM, scanner, inventários, overlay, fonte e wheel finais.
- alpine-runtime-audit.zip: arquivo original com integridade conferida; arquivos longos podem ser consultados nele mesmo quando a extração Windows não os materializa.
- Dockerfile.alpine-experimental, workflow-alpine.yml, prepare-experiment.py e inventory-experiment.py: configuração concreta do ensaio.
- analyze_evidence.py e verify_results.py: consolidação/verificação com biblioteca padrão; não integram a aplicação.
- EVIDENCE-SHA256.csv: manifesto local de entrega.

Comandos principais: git archive do candidato; uv sync --locked; uv build --wheel --no-build-isolation; uv pip check; Docker build por digest; apk update/upgrade/add; pytest --junitxml; Ruff/formatação/mypy; conexão psycopg verify-full; Trivy image e CycloneDX; consultas OSV e bases oficiais de segurança; conferência SHA256.

[Debian](https://github.com/liraneto1/DeepTradeSystem/actions/runs/44146961378) · [Alpine com instalador inicial](https://github.com/liraneto1/DeepTradeSystem/actions/runs/44147939259) · [Alpine com instalador atualizado](https://github.com/liraneto1/DeepTradeSystem/actions/runs/44149289640) · [Alpine mínimo final](https://github.com/liraneto1/DeepTradeSystem/actions/runs/44150219172).

Uma montagem inicial de teste detectou que o pacote binary havia permanecido por causa da instalação inexact; o ensaio foi corrigido para removê-lo explicitamente antes das verificações. Os resultados acima se referem às execuções concluídas identificadas, não à tentativa interrompida.
