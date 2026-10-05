# Task 3 - Relatorio de implementacao

## Status

Concluida. A trilha de filtros ativos agora usa `filterState` como fonte de verdade, e a renderizacao e reconstruida a partir do snapshot atual.

## Implementacao

- Adicionado botao `X` real para cada filtro, com `type="button"`, tooltip e `aria-label`.
- A remocao usa o indice da renderizacao atual, interrompe a propagacao e nao abre o editor.
- O corpo do item ativo reabre o editor de parametros quando o filtro suporta edicao.
- Confirmacoes de parametros atualizam o filtro existente quando a edicao foi aberta a partir da trilha; novos filtros continuam sendo adicionados pelos controles disponiveis.
- O payload continua sendo criado com `filterState.toPayload(func2byte)` e enviado como o mesmo `Uint8Array` numerico existente.
- Ao remover o ultimo filtro, a imagem local carregada e restaurada; sem imagem carregada, o estado vazio volta a ser exibido.
- Adicionados os testes de ordem apos remover o primeiro item e de payload vazio apos remover o ultimo filtro.

## Arquivos

- Modificado: `index.html`
- Modificado: `tests/ui-state.test.mjs`
- Nao alterados: `ui-state.mjs`, `main.py`, `funcs.py`

## Validacao

- `node --test tests/ui-state.test.mjs` - PASS, 11 testes.
- `python3 -m py_compile main.py funcs.py` - PASS.
- Checagem sintatica do script ES module embutido em `index.html` - PASS.
- `git diff --check` - PASS.

## Commit

- `feat: adiciona remocao acessivel de filtros`

## Preocupacoes

- A validacao automatizada nao inicia navegador nem WebSocket real; a interacao DOM foi revisada estaticamente e a sintaxe do modulo foi verificada.
- A imagem original e mantida por `ObjectURL` ate a proxima imagem ser selecionada; a troca de fonte para camera nao altera o protocolo.
