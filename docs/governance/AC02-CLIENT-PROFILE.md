# AC02 — Perfil de cliente PostgreSQL aprovado

Data: 17/11/2026. Baselines de referência TS-ARCH-GLOBAL-V1.0 e TS-ENG-I00-V1.0.
Vínculos: I00-02, apoio de I00-11, I00-AC02, TS-ST-001; TS-ADR-092/094/095/098.

## Decisão humana

O usuário aprovou o perfil Linux/Alpine sem LDAP/GSSAPI e autorizou sua
aplicação no DeepTradeSystem do BUSINESS, com preservação do fluxo Windows
e repetição das verificações antes de criar o novo commit candidato.

**Estado do perfil: APPROVED.** A implementação e suas novas evidências
permanecem **IN_REVIEW** até a apresentação e decisão correspondentes.

## Configuração

- Linux/amd64: Python 3.12.16, Psycopg C 3.3.8, libpq 18.7 do Alpine 3.24.
- Autenticação do recorte: senha/TLS; LDAP/GSSAPI/Kerberos/SSPI ausentes.
- Windows: Psycopg binário 3.3.8; build de cliente C não exigido.
- Build e runtime separados; runtime sem instaladores Python.
- Lockfile Python e APKs exatos, inventários e hashes das bibliotecas reais.
- PostgreSQL servidor e tratamento gosu permanecem em decisão separada.

A adoção refina o perfil técnico da stack PostgreSQL aprovada; não altera
os contratos transacionais, a arquitetura de domínios ou os critérios das
quatro histórias. Não há autorização de LIVE, deploy ou promoção automática.

## Limites da aprovação

A aprovação do perfil não significa aceite global de AC02, das quatro
histórias ou de G0. Permanecem a disposição dos riscos de segurança,
responsabilidades técnicas/QA, operadores e políticas de atualização e
retenção. Não foi concedida dispensa automática para avisos de build.

## Referências

- [Ensaio anterior e riscos](../evidence/ac02-maintained-client-ac51f91/RESULTADOS.md).
- [Proposta histórica agora autorizada no recorte acima](../evidence/ac02-maintained-client-ac51f91/PROPOSTA-ADOCAO.md).
- [Procedimento de instalação e verificação](../runbooks/client-profile.md).
- [Verificações da aplicação no BUSINESS](../evidence/ac02-profile-adoption/RESULTADOS.md).
