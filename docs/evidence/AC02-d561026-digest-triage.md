# AC02 Triagem do digest PostgreSQL e componentes Linux

**12/11/2026 · d561026f27fa3920699af41aeea6e1a60bcf89a6 · validação parcial.** LIVE permanece indisponível.

## Repetição da integração

A execução existente do SHA passou com 38 testes PostgreSQL em PAPER e LIVE_ENABLED=false. O workflow aceita push e pull request e usa postgres:17. Reexecutar esse job manteria a tag móvel. O host não tem Docker, Podman ou distribuição WSL disponível. A repetição por digest ficou pendente. [Execução existente](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43308853482/job/131499228992) · [Evidência anterior](AC02-d561026-linux-security.md)

No runner Linux amd64 com Docker, usar checkout descartável no SHA acima e sobrepor somente o campo image do serviço postgres para docker.io/library/postgres@sha256:6f7593c161689b6b02c78668b314af7da8811b592c5519108c57a49d0b6ad788. Usar projeto e volume descartáveis, senha de teste, loopback, TRADE_SYSTEM_ENVIRONMENT=PAPER, LIVE_ENABLED=false e RUN_POSTGRES_TESTS=1. Conferir a imagem resolvida no container e executar `uv sync --locked` e `uv run --no-sync pytest tests/integration`. Registrar SHA, digest, plataforma, contagem e resultado. A imagem auditada abaixo tem achados em aberto e carece de decisão de Segurança para uso no recorte de teste.

## Triagem da imagem auditada

| Achado | Disposição |
|---|---|
| CVE-2026-6653 · libxml2 | Debian confirma a versão trixie instalada como afetada e registra no-dsa. A aplicabilidade ao caminho PostgreSQL depende da exposição ao processamento de XML. A restrição a loopback reduz exposição no ensaio. Manter aberto até comprovar o recorte ou substituir por imagem corrigida. [Debian Security Tracker](https://security-tracker.debian.org/tracker/CVE-2026-6653) |
| CVE-2025-68121 · stdlib Go em gosu | O aviso exige retomada de sessão TLS em crypto/tls. A função de gosu como troca de usuário e execução de processo sugere baixa aplicabilidade a esse caminho. Confirmar o binário e os símbolos alcançáveis antes de registrar exceção. [Go Vulnerability Database](https://pkg.go.dev/vuln/GO-2026-4337) |
| 149 ocorrências altas | 27 com estado fixed na base, 118 affected e 4 fix_deferred. Fixed indica correção conhecida na base, não aplicada ao digest auditado. Priorizar stdlib Go, Kerberos e libxml2 pela concentração. Falta triagem de alcance e decisão por achado ou grupo com justificativa comum. |

Os resultados são do digest explícito indicado acima. O digest histórico do CI permanece sem confirmação. [Relatório Trivy](AC02-postgres-6f7593c-trivy.json)

## Nativos e build Linux

- O wheel CPython 3.12 manylinux x86_64 de psycopg-binary 3.3.8 foi baixado e teve SHA-256 conferido contra o lockfile: a7cdba018e4decf3837793c1e18dbe3dd71709adef54892ab83d81c00e866dc3. A inspeção estática identificou 15 bibliotecas incorporadas, incluindo libpq, libcrypto/libssl, Kerberos/GSSAPI, LDAP, SASL, PCRE, SELinux e bibliotecas de suporte. Os nomes e SONAMEs não identificam todas as versões de origem ou backports. Falta confirmar o wheel efetivamente carregado no runner, obter versões e procedência das bibliotecas e triar os avisos aplicáveis. O inventário Windows não transfere cobertura para Linux.
- Hatchling 1.28.0 está fixado no pyproject.toml. O CI Linux registra build bem-sucedido. Falta exportar as versões efetivamente resolvidas no ambiente isolado de build Linux e consultar os avisos para esse conjunto. A consulta OSV anterior abrangeu os cinco pares de build observados no cache Windows.

**AC02 permanece em validação.** A repetição com digest, a triagem remanescente e o parecer de Engenharia, QA e Segurança ainda são necessários. G0 segue aberto.
