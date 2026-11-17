# Proposta de adoção — cliente Psycopg/libpq no recorte I00

Estado: PROPOSED, para revisão do usuário. Nenhuma alteração de candidato aplicada por esta proposta.

## Escolha recomendada

Perfil de execução Linux/amd64 com Python 3.12.16, Psycopg C 3.3.8 e libpq 18.7 do Alpine 3.24, com OpenSSL mantido pelo fornecedor. Build e runtime separados; instaladores Python e suas cópias embutidas ficam fora do runtime. Servidor permanece PostgreSQL 17, em decisão separada da imagem/gosu.

O perfil serve ao recorte atual de banco local, dados sintéticos, autenticação por senha e TLS. O libpq Alpine inspecionado é compilado sem LDAP/GSSAPI. A decisão sobre essa limitação precede qualquer adoção; não há alegação de equivalência integral ao cliente binary original.

## Mudanças concretas propostas para um futuro candidato

| Arquivo / área | Mudança proposta | Verificação de adoção |
|---|---|---|
| pyproject.toml | Selecionar extra c no Linux e conservar binary fora do Linux; manter Psycopg 3.3.8 nesta mudança. | Resolver todas as plataformas suportadas, conferir extras por marcador e executar instalação Windows antes de declarar suporte preservado. |
| uv.lock | Acrescentar psycopg-c 3.3.8 e o sdist com hash, mantendo as versões comuns já verificadas. | Instalação locked no perfil Linux e comparação de versões; nenhuma atualização transitiva incidental. |
| deploy/docker/client-runtime.Dockerfile, novo | Incorporar a receita experimental revisada, com bases por digest, APKs identificados e compilação em estágio separado. | Mesmos binários C na suíte e runtime; testes, TLS, inventário e scanner no novo SHA. |
| .github/workflows/ci.yml ou workflow específico | Tornar obrigatória a verificação do perfil qualificado e inventários de runtime/build. | Falha de build/teste bloqueia progressão; registrar digest/ID e proveniência dos artefatos. |
| Documentação de compatibilidade e operação | Registrar Linux/amd64 qualificado, senha/TLS, ausência de LDAP/GSSAPI e fluxo Windows de desenvolvimento. | Revisão técnica/QA; não transferir a conclusão Linux para Windows ou ARM. |
| Evidence Bundle | Vincular o novo SHA, wheel C, bibliotecas, imagem, scanner e riscos aceitos. | Conferência de integridade e decisão humana de segurança/aceite. |

Especificação sugerida de dependências para revisão, ainda não aplicada:

    "psycopg[c]==3.3.8; sys_platform == 'linux'",
    "psycopg[binary]==3.3.8; sys_platform != 'linux'",

O ensaio executado usou o equivalente Linux em uma cópia temporária do pyproject, não esses marcadores multiplataforma. Os marcadores deverão ser verificados no novo candidato antes de adoção. O perfil Linux qualificado é o container identificado; instalar c em qualquer outra distribuição não garante as mesmas versões nativas.

## Decisões necessárias antes da implementação

1. Confirmar que o recorte I00 pode usar senha/TLS sem LDAP, GSSAPI/Kerberos ou SSPI. Se esses recursos forem necessários, não adotar esta configuração: preparar alternativa mantida que os preserve.
2. Confirmar Linux/amd64 em container como ambiente qualificado deste recorte; manter Windows como desenvolvimento sujeito a sua própria verificação.
3. Designar responsabilidade por atualização de imagem, APKs, Psycopg C e revisão de vulnerabilidades. Atualizar APKs exige reconstrução e repetição das verificações.
4. Revisar e registrar a disposição de segurança do aviso Windows de setuptools 83.0.0 no build Linux. A versão é exigida no pyproject do sdist upstream 3.3.8; não foi alterada silenciosamente.
5. Definir responsáveis técnico/QA e decidir separadamente a imagem PostgreSQL/gosu já ensaiada.

## Limites

A receita experimental e os artefatos de wheel são revisáveis nesta pasta. A imagem experimental não foi publicada nem salva como imagem distribuível; seu ID serve para identificar a execução. Para adoção é necessário produzir e preservar uma imagem no novo candidato, com política de retenção e reconstrução.

Não executar sincronização cega do checkout BUSINESS com as cópias de teste. As modificações existentes do usuário permanecem preservadas. O aceite das quatro histórias e G0 não são concedidos por esta proposta.
