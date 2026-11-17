# Cliente PostgreSQL — Linux/Alpine e desenvolvimento Windows

Perfil Linux/amd64 sem LDAP/GSSAPI aprovado pelo usuário em 17/11/2026, para I00.
[Decisão e limites](../governance/AC02-CLIENT-PROFILE.md).

## Windows

O comando existente continua sendo:

    uv sync --locked

No Windows, a resolução seleciona psycopg[binary] 3.3.8. Não é necessário
compilar psycopg-c nem instalar headers PostgreSQL. O grupo build mantém
setuptools 83.0.0 restrito ao Linux.

Para reproduzir os controles de build do CI em um ambiente normal .venv:

    uv sync --locked --only-group build
    uv sync --locked --group build --no-build-isolation
    uv run --no-sync ruff check src infrastructure apps tests tools/client_profile
    uv run --no-sync ruff format --check src infrastructure apps tests tools/client_profile
    uv run --no-sync mypy
    uv run --no-sync pytest
    uv build --no-sources --no-build-isolation

Em ambiente alternativo, passar também --python <interpretador> ao uv build;
a seleção de ambiente do build deve ser conferida. Integrações PostgreSQL
exigem instância descartável e RUN_POSTGRES_TESTS=1. Sem isso são puladas,
não aprovadas. Esta preservação do fluxo não representa homologação de
segurança dos DLLs Windows.

## Linux qualificado

Python 3.12.16, Psycopg C 3.3.8, libpq 18.7-r0 e Alpine 3.24 em amd64.
Bases Python/uv por digest e conjunto completo de APKs não virtuais fixado
em deploy/docker/client-apk-lock.json. Resolução diferente falha; não há
atualização silenciosa para outro conjunto.

Compilar a partir da raiz do repositório:

    docker build --platform linux/amd64 --target runtime -f deploy/docker/client-runtime.Dockerfile -t deeptrade-client:review .

Para repetir build, qualidade, testes com PostgreSQL descartável, TLS,
identidade nativa, SBOM e scanner:

    bash tools/client_profile/verify.sh /caminho/absoluto/fora-do-contexto/evidencias

O diretório de evidências deve ficar fora do contexto de build para não
realimentar seus próprios artefatos. A porta local 55432 precisa estar livre.
O script cria e remove somente seu container e volume descartáveis.
A imagem do servidor PostgreSQL/gosu é uma decisão separada; seu digest de
teste permanece explícito no script. Credenciais e chave privada TLS são
temporárias; a chave privada não entra nos artefatos.

O alvo test usa as ferramentas do grupo build e salva APKs, fonte e wheel
do cliente. O mesmo wheel é instalado no ambiente de teste e no runtime.
O alvo runtime não contém pip, setuptools ou wheel, nem os wheels de bootstrap
ensurepip. Atualizações exigem reconstrução da imagem.

O comando padrão inicia a API diagnóstica em 127.0.0.1:8000 dentro do container.
Uma eventual configuração de rede/serviço deve respeitar o ambiente local
aprovado, com conta, supervisão e operadores definidos. Nenhum serviço é
instalado automaticamente.

## Compatibilidade e segurança

- Linux usa extra c; outros sistemas conservam binary, todos em 3.3.8.
  Somente Windows e Linux/amd64 fazem parte das verificações deste recorte.
- O libpq Alpine aprovado não oferece LDAP, GSSAPI/Kerberos ou SSPI.
  Senha e TLS são as capacidades de autenticação verificadas.
- Linux em outra distribuição pode resolver outras bibliotecas nativas.
  Não herdar automaticamente a qualificação do container.
- O build Linux usa setuptools 83.0.0 conforme exigência upstream do sdist
  Psycopg C. O aviso específico de Windows continua para disposição de
  Segurança; esse setuptools não é instalado no Windows nem no runtime.
- Cada nova ocorrência retornada pelo scanner do runtime faz a verificação
  falhar. Isso não concede aceite humano de AC02 nem de qualquer gate.
- A identidade dos APKs deve ser atualizada deliberadamente com inventário,
  revisão de vulnerabilidades, testes e evidências. Se versões deixarem de
  estar disponíveis no repositório, a construção falha. Os APKs capturados
  no CI auxiliam a reconstrução; ainda é necessário definir retenção e owner.

O CI publica como artefato o runtime testado, inventários e hashes. Esse
artefato de teste não é deploy nem promoção automática. LIVE permanece
desabilitado e nenhuma credencial operacional é utilizada.
