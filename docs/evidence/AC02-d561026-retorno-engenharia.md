# AC02 — Retorno de Engenharia para o candidato d561026

**13/11/2026 · Validação parcial.** Candidato
`d561026f27fa3920699af41aeea6e1a60bcf89a6`. SHA-256 do lockfile
`e40093ac899ba45d0d9290942cb66553fc02722d55f7cceeba70f26713970919`.
LIVE permanece indisponível. AC02 aguarda parecer e G0 segue aberto.

## PostgreSQL Linux amd64

- O SHA-256 calculado sobre os bytes do manifesto OCI é
  `6f7593c161689b6b02c78668b314af7da8811b592c5519108c57a49d0b6ad788`.
  O índice OCI `sha256:846a7ddaa67a4b354ae1d21087b683901aa6113a4ed626d3787cfbf6c85e3e07`
  associa esse manifesto a Linux amd64 e PostgreSQL 17.12. O digest
  da configuração é `sha256:140936e8665d5274aa58df31b722693b4b451c541bb0f1a263a345d424bfacb4`,
  idêntico ao ImageID do Trivy. O acesso direto ao blob de configuração
  retornou HTTP 404. A plataforma foi confirmada pelo índice.
- A API do GitHub confirmou o sucesso do job e de suas etapas. O SHA
  `5c431bb37273c459921ce7000e40135a9df0d615` identifica a definição do
  workflow. O workflow verifica o checkout de `d561026`, exige
  Linux amd64 e compara a identidade do container à da imagem
  puxada pelo digest. A contagem de 38 testes vem do handoff.
  A API de logs retornou HTTP 403 nesta revisão.
  [Job](https://github.com/liraneto1/DeepTradeSystem/actions/runs/43324339962/job/131552874577)
  · [Workflow](https://github.com/liraneto1/DeepTradeSystem/blob/5c431bb37273c459921ce7000e40135a9df0d615/.github/workflows/ac02-postgres-digest.yml)
- O relatório Trivy 0.76.2, base de 12/11/2026 às 18:57:38 UTC,
  tem SHA-256 `83e160d10c21c517d675b51b3dfaac6949e174aa5f0d6df4b12032860ec498b6`.
  A [matriz CSV](AC02-d561026-postgres-triage.csv) vincula as 610
  ocorrências ao alvo, componente, versão e tratamento proposto.
  As classificações genéricas da matriz sinalizam alcance pendente.
  [Relatório bruto](AC02-postgres-6f7593c-trivy.json)
- **libxml2, CVE-2026-6653.** Debian identifica trixie como afetado.
  O caminho requer processamento de XML. O banco descartável em
  loopback reduz a exposição externa. Engenharia precisa confirmar
  a disponibilidade do processamento XML e quais clientes poderiam
  alcançá-lo durante o ensaio. Segurança decide o risco residual
  ou exige troca do digest e repetição da integração.
  [Debian Security Tracker](https://security-tracker.debian.org/tracker/CVE-2026-6653)
- **gosu, CVE-2025-68121.** O aviso requer o caminho de retomada de
  sessão de `crypto/tls`. O uso de gosu na inicialização para trocar
  de usuário sugere baixa exposição nesse recorte. Engenharia deve
  comprovar os símbolos e o caminho de execução do binário exato.
  Segurança decide eventual exceção e sua validade.
  [Go Vulnerability Database](https://pkg.go.dev/vuln/GO-2026-4337)

## Componentes nativos e build Linux

O wheel público de psycopg-binary 3.3.8 para CPython 3.12 manylinux
x86-64 foi baixado e conferido contra o lockfile. O
[inventário estático](AC02-d561026-linux-wheel-static.json) registra
URL, hash do wheel e hashes de 17 arquivos ELF, incluindo duas
extensões Python e 15 bibliotecas. A seleção e o carregamento no
runner, as versões efetivas e os backports ainda exigem evidência.
Avisos exclusivos do servidor PostgreSQL exigem triagem separada
dos avisos que atingem libpq.

O build Linux anterior passou segundo a
[evidência existente](AC02-d561026-linux-security.md). A auditoria
do ambiente efetivo continua pendente. O Windows desta revisão
está sem distribuição WSL ou Docker disponível. A API do run por
digest não listou artefatos. Ainda faltam a captura do CPython e
do uv efetivamente usados, a resolução isolada de Hatchling e
transitivas, a consulta de avisos dessas versões e os hashes e logs
do wheel e sdist produzidos em Linux.

**Para decisão:** Engenharia coleta os artefatos Linux no candidato
e fecha a análise de alcance. QA confere a vinculação ao candidato,
à plataforma, ao lockfile e ao digest. Segurança decide as
correções ou exceções com validade e responsável. Esses pareceres
são necessários antes de submeter AC02 a aceite.
