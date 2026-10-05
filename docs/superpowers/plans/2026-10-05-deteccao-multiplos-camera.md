# Deteccao de multiplos objetos na camera Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detectar multiplos objetos na camera e tocar `detection.mp3` uma vez quando um objeto novo surgir.

**Architecture:** O backend identifica componentes conectados/contornos em cada frame do filtro Tracking, desenha uma caixa por objeto e mantem IDs por proximidade. O WebSocket continua enviando PNGs e acrescenta uma mensagem JSON de metadados; o frontend mantem IDs anteriores e reproduz o audio apenas para IDs novos.

**Tech Stack:** Python 3, OpenCV, NumPy, WebSocket existente, HTML, JavaScript ES modules, Node.js test runner.

## Global Constraints

- Preservar o protocolo numerico existente para filtros e processamento de imagens.
- Nao alterar o comportamento dos filtros estaticos.
- Usar `detection.mp3` existente na raiz do projeto como arquivo de audio.
- Nao tocar audio repetidamente para o mesmo objeto persistente.
- Falhas de reproducao de audio nao podem interromper o processamento.
- Preservar alteracoes locais existentes que nao pertencam a esta tarefa.
- Usar ASCII em codigo novo, exceto o arquivo binario de audio.

---

### Task 1: Criar deteccao multipla testavel

**Files:**
- Modify: `funcs.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Produces `detect_objects(img, min_area=400) -> tuple[ndarray, list[dict]]`.
- Cada item de deteccao possui `id`, `bbox` e `center`.
- Produces `match_detections(previous, current, max_distance=80) -> list[dict]`.

- [ ] Escrever testes para dois componentes separados e para IDs persistentes por proximidade.
- [ ] Rodar `.venv/bin/python -m unittest tests.test_main` e confirmar a falha inicial.
- [ ] Implementar deteccao por threshold/contornos, filtragem por area minima e caixas por objeto.
- [ ] Implementar matching deterministico por distancia entre centros, atribuindo IDs novos quando nao houver correspondencia.
- [ ] Rodar os testes e confirmar todos passam.
- [ ] Fazer commit `feat: adiciona deteccao multipla de objetos`.

### Task 2: Integrar deteccao no processamento de video

**Files:**
- Modify: `main.py`
- Modify: `funcs.py` se necessario
- Test: `tests/test_main.py`

**Interfaces:**
- `trackVideo` deixa de depender de um unico tracker OpenCV.
- O processamento de um frame retorna imagem anotada e deteccoes atuais para o handler.

- [ ] Substituir o estado global `tracker` por estado de deteccoes anteriores por conexao.
- [ ] Aplicar o filtro Tracking sem chamar uma funcao com assinatura incompleta.
- [ ] Enviar PNG como antes e JSON com `{ "type": "detections", "objects": [...] }` depois do PNG.
- [ ] Limpar deteccoes quando a conexao, camera ou filtro Tracking for encerrado.
- [ ] Testar compilacao Python e o erro reproduzido de tracking.
- [ ] Fazer commit `feat: integra deteccao multipla no video`.

### Task 3: Reproduzir audio para objetos novos

**Files:**
- Modify: `index.html`
- Modify: `ui-state.mjs`
- Modify: `tests/ui-state.test.mjs`
- Include: `detection.mp3`

**Interfaces:**
- `getNewDetectionIds(previousIds, currentObjects) -> string[]`.
- O handler JSON de deteccoes chama `playDetectionAudio` somente quando houver IDs novos.

- [ ] Escrever testes para objeto persistente, objeto novo e reaparecimento depois de lista vazia.
- [ ] Rodar `node --test tests/ui-state.test.mjs` e confirmar a falha inicial.
- [ ] Implementar helper puro de IDs e audio `new Audio('./detection.mp3')` com `play().catch(() => {})`.
- [ ] Integrar mensagens JSON sem confundir com respostas PNG.
- [ ] Rodar testes Node, sintaxe inline e `git diff --check`.
- [ ] Fazer commit `feat: toca audio em novas deteccoes`.

### Task 4: Validacao e documentacao

**Files:**
- Modify: `README.md`
- Test: `tests/test_main.py`, `tests/ui-state.test.mjs`

- [ ] Documentar que o filtro Tracking detecta varios objetos e usa `detection.mp3`.
- [ ] Rodar `.venv/bin/python -m unittest tests.test_main`.
- [ ] Rodar `node --test tests/ui-state.test.mjs`.
- [ ] Rodar `.venv/bin/python -m py_compile main.py funcs.py`.
- [ ] Rodar `git diff --check` e verificar apenas arquivos planejados, alem de alteracoes locais preexistentes.
- [ ] Fazer commit `docs: documenta deteccao e audio da camera`.
