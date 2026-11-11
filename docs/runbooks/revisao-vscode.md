# Revisão do projeto no VS Code

Abra a pasta `DeepTradeSystem` escolhida como checkout principal em **Arquivo → Abrir Pasta**. O painel **Explorador** mostra os arquivos. Abra o `README.md` e pressione **Ctrl+Shift+V** para ver o Markdown formatado. A imagem também pode ser aberta pelo Explorador. Os originais Word ficam em `acervo-local/` e podem ser abertos no Word pelo Explorador de Arquivos.

## Como conferir o trabalho

1. Use **Ctrl+Shift+G** para abrir **Controle do Código-Fonte**. Clique em um arquivo alterado para comparar as versões.
2. Um **commit** é um registro de alterações revisáveis. Uma **branch** é uma linha de trabalho. Confira a branch no canto inferior esquerdo e, no terminal integrado, use:

   ```powershell
   git status --short --branch
   git log -5 --oneline
   git show --stat HEAD
   ```

3. Abra [a visão inicial](../architecture/visao-inicial.md), [o backlog](../02-I00-BACKLOG.md) e [as evidências](../evidence/I00-bootstrap.md) para ligar o objetivo, os arquivos e os testes.
4. No GitHub, abra a aba **Actions** e confira a execução da mesma branch. Um teste local e uma execução no GitHub são evidências distintas.

## Como rastrear cada etapa

Antes de alterar arquivos, registre o pacote do backlog, os arquivos previstos, as dependências e como verificar a entrega. Ao concluir, registre em `docs/evidence/` os comandos executados, os resultados e os itens pendentes. Use o identificador do pacote no commit. A aprovação humana deve ficar registrada antes de iniciar uma etapa que dependa dela.
