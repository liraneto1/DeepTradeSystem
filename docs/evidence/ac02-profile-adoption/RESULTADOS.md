# AC02 — Aplicação do perfil Linux/Alpine no BUSINESS

Registro histórico da revisão anterior ao commit. Alterações e resultados
aprovados pelo usuário, com as pendências mantidas, em 17/11/2026.
[Registro da aprovação e autorização do commit](APPROVAL.md).

17/11/2026. Estado: implementação e verificações concluídas, **IN_REVIEW antes do commit candidato**.
Projeto: DeepTradeSystem do BUSINESS. Perfil aprovado pelo usuário nesta conversa.

## Resultado

O perfil foi aplicado no working tree. Linux seleciona Psycopg C 3.3.8;
Windows conserva Psycopg binário 3.3.8 e o comando habitual uv sync --locked.
O runtime Linux/amd64 usa Python 3.12.16 e libpq 18.7-r0 do Alpine 3.24,
sem LDAP/GSSAPI, com build separado e sem instaladores Python no runtime.

As verificações passaram: 164 testes no Windows local, 164 no Linux/Alpine,
qualidade, tipos, build, três casos TLS e zero ocorrências retornadas pelo
scanner do runtime. A imagem efetivamente testada foi preservada e verificada.

**Nenhum commit candidato foi criado.** HEAD local e branch candidata remota
review/ts-st-001-004-ac51f91 continuam em
ac51f91cfc08dadae3a3bb411908b0b9a26f11af. O índice não contém alterações staged.
As modificações anteriores do usuário foram preservadas.

## Arquivos aplicados

[Lista exata dos 17 arquivos](FILES-CHANGED.csv) e
[comparação dos blobs com a fotografia validada](SOURCE-COMPARISON.csv).

| Área | Arquivos | Resultado |
|---|---|---|
| Dependências | pyproject.toml, uv.lock | Extras por plataforma; grupo build fixado; seis pacotes acrescentados, nenhuma versão existente alterada. |
| Runtime | deploy/docker/client-runtime.Dockerfile, client-apk-lock.json | Bases por digest, APKs exatos, compilação separada, cliente C e runtime sem pip/setuptools/wheel. |
| Verificação | tools/client_profile/{build,install_apks,inventory,verify,tls}.py e verify.sh | Fonte do lockfile por hash, inventário real, igualdade nativa, testes, TLS, SBOM, scanner e imagem salva. |
| CI | .github/workflows/ci.yml | Jobs de qualidade, Windows e Linux/Alpine; este último depende dos dois anteriores. Nova ocorrência no scanner do runtime falha a verificação. |
| Empacotamento | .dockerignore, .gitignore e configuração sdist no pyproject | Evidências, dados, acervo e referências externas não entram no sdist; binários brutos desta auditoria ficam fora do futuro commit. |
| Documentação | README.md, TS-ST-001.md, AC02-CLIENT-PROFILE.md, client-profile.md | Aprovação do perfil, limites, instalação Windows e reprodução do perfil Linux registrados. |

Os arquivos de baseline 00–06 não foram alterados. A mudança pertence a I00-02 /
I00-AC02 com apoio das verificações de I00-11. Os contratos e o código de domínio
permanecem iguais.

## Dependências e controle de build

As 60 relações nome/versão que já existiam no lockfile foram preservadas.
Foram acrescentados psycopg-c 3.3.8, editables 0.6, hatchling 1.28.0,
setuptools 83.0.0, trove-classifiers 2026.9.21.13 e wheel 0.48.0.
Setuptools 83 tem marcador exclusivo de Linux. Binary continua no lockfile
para o Windows, mas não é instalado no runtime Linux.

Editables é necessário ao build editável do Hatchling e foi fixado no grupo
build após a instalação limpa revelar essa dependência dinâmica. Não houve
instalação avulsa não registrada para fazer os testes passarem.

O build usa primeiro uv sync --locked --only-group build e depois
uv sync --locked --group build --no-build-isolation. O sdist de Psycopg C
é obtido do URL/hashes do uv.lock. O mesmo wheel C é instalado no ambiente de
testes e no venv mínimo; o fechamento de dependências é conferido.

Há 92 APKs não virtuais fixados no estágio de teste e 38 no runtime.
A resolução efetiva é comparada ao conjunto completo aprovado. Os APKs do
estágio de teste foram preservados no ZIP. Se versões exatas deixarem de estar
disponíveis, o build falha; não atualiza silenciosamente o perfil.

## Verificações e evidências

[CI final — SUCCESS](https://github.com/liraneto1/DeepTradeSystem/actions/runs/44155830173).
Fotografia exclusiva de validação:
e409e39f2d8afec88c31df490df131aa01a46088, branch
review/ac02-profile-adoption-validation. Esse SHA identifica o ensaio remoto;
não houve promoção à branch candidata nem movimento do HEAD do BUSINESS.

Os 17 blobs dessa fotografia coincidem com os 17 arquivos atuais do BUSINESS.
Os 12 arquivos de entrada usados no build/verificação também coincidem em
SHA256 com normalização de fim de linha LF.

| Ambiente / controle | Resultado real |
|---|---|
| Windows, comando habitual | Instalação limpa uv sync --locked aprovada; cliente binary; import do projeto aprovado. |
| Windows, build controlado | Instalação do grupo build, Ruff, formatação, mypy e sdist/wheel aprovados. Sem psycopg-c ou setuptools 83 no ambiente. |
| Windows, integração local | Python 3.12.12, Psycopg 3.3.8, libpq binário 18.4, PostgreSQL 17.11 descartável: 164 passed, zero skips/falhas/erros; 66,84 s no console. Banco encerrado ao final. |
| Windows, CI | 115 passed, 49 skipped; qualidade, tipos, build e seleção binary aprovados. Os 49 skips são integrações não executadas nesse job, cobertas no Linux e no Windows local. |
| Ubuntu, qualidade auxiliar | 115 passed, 49 skipped; qualidade, tipos e build aprovados. Este job não qualifica as bibliotecas nativas do host Ubuntu para operação. |
| Linux/Alpine, perfil qualificado | 164 passed, zero skips/falhas/erros; 30,89 s. Integrações com PostgreSQL 17.12 descartável e dados sintéticos. |
| Ruff / formatação | Aprovados; 103 arquivos formatados conforme esperado. |
| Mypy | Sem problemas nos 98 arquivos configurados de aplicação/testes. |
| Identidade nativa | 39 arquivos comuns entre teste e runtime, incluindo as duas extensões C, com hashes idênticos. |
| TLS | Conexão SQL verify-full com TLS 1.3; nome incorreto e raiz de confiança ausente rejeitados. |
| Runtime | Implementação c; libpq de compilação e execução 180007, isto é, 18.7; ausência de binary e instaladores verificada. |
| Segurança do runtime | Trivy por digest, sem ignore de CVE nem filtro por severidade: zero ocorrências retornadas; SBOM CycloneDX preservado. |
| Integridade | 199 arquivos do manifesto remoto conferidos sem divergências; 21 blobs OCI verificados pela cadeia de digests. |

O sdist Windows final tem 2.826.247 bytes. A conferência do arquivo confirma que
não contém evidências geradas, dados ou diretório runtime. O empacotamento anterior
incluía grandes artefatos de auditoria; isso foi corrigido antes desta rodada final.

Os números acima são repetições da mesma suíte de 164 testes, não novos requisitos
ou 328 critérios distintos. O CI anterior à revisão de empacotamento também passou,
mas o parecer usa a fotografia final identificada acima.

## Imagem testada preservada

Arquivo: artifacts/client-runtime.tar.

- ID / índice OCI executado e auditado:
  sha256:03d3dea2e1ae064bcd8bac34190b4cf415fae42115157041be065fcc662364be.
- Digest da configuração do container:
  sha256:7ffb6d88fcd3aeccbdc45ff1404724b7ad26cf8fab55f01e1be9a7334d983fcb.
- SHA256 do tar:
  df2300ad541892d5dadb731e159fd970adc48019a153e0de7c0cf412183305e2.
- Artefato GitHub 14360663469, 310.738.644 bytes.
- SHA256 do ZIP original linux-profile.zip:
  370c7a4d78796c666cbd1b618853b75fe99ddf939a24973b81f27d6e6ae37aee.

O Docker utilizado identifica a imagem pelo índice OCI, que é diferente do digest
da configuração. A verificação confirmou o índice, os manifests, a configuração
e as camadas; não presumiu que esses identificadores fossem iguais.

A imagem foi salva como artefato de teste, sem publicação em registry ou deploy.
A fonte, wheel C, APKs e inventários completos permanecem no ZIP original.
Os relatórios, o wheel e a imagem foram materializados em artifacts/ para revisão.
Arquivos com caminhos longos podem ser consultados no ZIP, cuja verificação não
depende da extração Windows.

## Segurança e pendências restantes

A consulta OSV aos 65 pares externos do lockfile retornou apenas
GHSA-xmj3-9gf7-h52w para setuptools 83.0.0. O aviso descreve um caminho legado
de instalação de wheel específico de Windows. Essa versão é exigida pelo
sdist upstream do Psycopg C, é utilizada somente no build Linux e não está
no Windows nem no runtime. A disposição de não aplicabilidade nesse recorte
continua para revisão de Segurança; não registramos uma dispensa automática.

Permanecem:

1. **Aceite de segurança:** revisar o aviso de build e os riscos residuais;
   zero ocorrências no runtime é resultado da base consultada, não prova de
   ausência universal de vulnerabilidades ou aprovação de AC02.
2. **Windows:** fluxo funcional preservado. Os DLLs Windows e o PostgreSQL 17.11
   usados na regressão local não receberam homologação de segurança neste
   trabalho. O runtime qualificado é Linux/amd64 com servidor 17.12 de teste.
3. **Operação:** definir responsáveis técnicos, QA, operadores, conta/serviço,
   supervisão e destino de alertas. Este trabalho não instala serviços.
4. **Atualização e retenção:** definir owner e rotina de reconstrução e
   revalidação de Python/base, APKs, Psycopg e ferramentas. O ZIP/imagem estão
   preservados; uma reconstrução online continua sujeita à disponibilidade
   das versões fixadas nos repositórios.
5. **Servidor PostgreSQL/gosu:** a configuração do servidor não foi modificada.
   O ensaio usa o digest PostgreSQL 17.12 já registrado; a decisão de adoção
   da imagem com gosu recompilado permanece separada.
6. **Cobertura:** Linux/amd64, senha/TLS e a suíte descrita foram verificados.
   Não houve ensaio de LDAP/GSSAPI, ARM, carga operacional representativa,
   qualificação PAPER ou avaliação de G0.
7. **Cadeia de fornecimento:** hashes, origens, APKs, wheel e imagem foram
   preservados; não foi concluída homologação de assinatura/atestação e
   segurança de toda a cadeia de compilação.

A aprovação do perfil já está registrada; não está sendo solicitada novamente.
O aceite técnico das quatro histórias continua dependendo das revisões e
responsabilidades correspondentes. LIVE permanece desabilitado.

## Comandos e entrega para revisão

Principais comandos executados:

- uv lock e uv lock --check; comparação das versões antigas e novas.
- Instalação Windows normal e com grupo build em venvs temporários separados.
- Ruff check/format, mypy, uv build e pytest --junitxml.
- PostgreSQL Windows iniciado e encerrado em diretório descartável, com senha
  temporária e loopback; teste Linux com container e volume descartáveis.
- bash tools/client_profile/verify.sh no CI: builds por digest, APKs por versão,
  testes, TLS, scanner, SBOM, salvamento de imagem e manifesto.
- Consulta OSV; verificação SHA256 do ZIP/manifesto e cadeia OCI.
- Conferência dos 17 blobs, índice sem staged changes e HEAD/branch candidata
  preservados em ac51f91.

VERIFICATION.json registra os controles finais; lock-delta.json, osv-*.json,
SOURCE-COMPARISON.csv, FILES-CHANGED.csv e os logs/JUnit Windows complementam
os artefatos Linux. EVIDENCE-SHA256.csv cobre os arquivos locais de revisão.
Os binários brutos estão ignorados pelo Git.

As alterações estão prontas para a revisão solicitada antes do novo commit
candidato. Não foi criado commit candidato, merge, deploy ou aprovação de gate.
