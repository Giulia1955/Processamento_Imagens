# Correcoes de medidas e deteccao YOLO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir area, perimetro e diametro e contar objetos reconhecidos pela YOLO em cada frame de video.

**Architecture:** `funcs.py` tera uma rotina compartilhada para componentes e um adaptador YOLO. `main.py` preservara os codigos numericos e o protocolo WebSocket, usando deteccoes atuais e IDs por proximidade. Os testes usarao imagens sinteticas e um detector falso, sem depender da rede.

**Tech Stack:** Python 3, NumPy, OpenCV, `ultralytics`, pytest, WebSocket existente e JavaScript atual.

## Global Constraints

- Preservar o protocolo numerico dos filtros e as mensagens PNG existentes.
- Usar componentes conectados/contornos para imagem binaria e YOLO para video colorido.
- Carregar o modelo sob demanda e permitir `YOLO_MODEL_PATH`.
- Nao treinar modelo customizado nem prometer classes ausentes no modelo.
- Frames sem deteccoes retornam lista vazia; falhas geram erro explicito sem travar o backend.
- Manter IDs estaveis por proximidade e enviar a lista atual ao navegador.

---

### Task 1: Criar componentes e medidas compartilhadas

**Files:** `funcs.py`, `tests/test_main.py`

**Interfaces:** `extract_components(img) -> list[dict]`, com `label`, `mask`, `contour`, `area`, `perimeter`, `diameter`, `bbox` e `center`; `area`, `perimeter`, `diameter` e `objects` continuam retornando imagens BGR anotadas.

- [ ] **Step 1: Write the failing tests**

Adicionar uma imagem binaria com dois retangulos e verificar `len(components) == 2`, areas `[100, 400]`, perimetros e diametros positivos. Adicionar outro teste que execute `area`, `perimeter`, `diameter` e `objects` e verifique forma `(30, 30, 3)` e tipo `uint8`.

- [ ] **Step 2: Run tests and verify failure**

Run: `.venv/bin/python -m pytest tests/test_main.py -k "components or measurement" -q`

Expected: FAIL porque `extract_components` nao existe e as funcoes atuais nao compartilham componentes.

- [ ] **Step 3: Implement one OpenCV extraction path**

Normalizar entrada para mascara binaria `uint8`, chamar `cv2.connectedComponentsWithStats(mask, 8)`, ignorar o label zero, obter o contorno por mascara do componente, calcular area pelos pixels, perimetro com `cv2.arcLength` e diametro com `2 * radius` de `cv2.minEnclosingCircle`. Armazenar caixa e centro. Rejeitar `pixelSize <= 0` com `ValueError`.

- [ ] **Step 4: Route all image filters through it**

Desenhar a origem em BGR, anotar cada componente na origem da caixa e usar a medida solicitada no texto. `objects` deve numerar todos os componentes a partir de 1. Remover as filas manuais.

- [ ] **Step 5: Run focused and existing tests**

Run: `.venv/bin/python -m pytest tests/test_main.py -q`

Expected: PASS, incluindo os testes existentes de tracking e deteccao.

- [ ] **Step 6: Commit**

```bash
git add funcs.py tests/test_main.py
git commit -m "fix: calcula medidas por componentes conectados"
```

### Task 2: Integrar um adaptador YOLO testavel

**Files:** `funcs.py`, `tests/test_main.py`, `requirements.txt` (criar se ausente)

**Interfaces:** `YoloDetector(model_path=None, confidence=0.25)` com `detect(frame) -> list[dict]`; cada item tem `class_name`, `confidence`, `bbox`, `center` e `area`; `detect_objects(frame, detector=None) -> tuple[np.ndarray, list[dict]]`.

- [ ] **Step 1: Write the failing adapter test**

Criar `FakeDetector.detect` que retorna `person` e `cell phone` com duas caixas. Chamar `detect_objects(frame, detector=FakeDetector())` e verificar mesma forma do frame, duas deteccoes e nomes preservados.

- [ ] **Step 2: Run and verify failure**

Run: `.venv/bin/python -m pytest tests/test_main.py -k detector -q`

Expected: FAIL porque `detect_objects` nao aceita adaptador YOLO.

- [ ] **Step 3: Add dependency and lazy loader**

Adicionar `ultralytics` a `requirements.txt`. Implementar `YoloDetector` com importacao e instancia do `YOLO` somente no primeiro `detect`, usando `YOLO_MODEL_PATH` quando nao houver caminho explicito. Converter caixas e nomes para valores Python e filtrar confianca abaixo do limite.

- [ ] **Step 4: Annotate results and preserve empty frames**

Fazer `detect_objects` chamar o detector, desenhar caixa, classe, confianca e total. Retornar frame BGR e lista vazia quando nao houver resultado. Converter falhas do detector em `RuntimeError` com mensagem clara.

- [ ] **Step 5: Run adapter tests without model download**

Run: `.venv/bin/python -m pytest tests/test_main.py -k detector -q`

Expected: PASS sem rede ou pesos reais.

- [ ] **Step 6: Commit**

```bash
git add funcs.py tests/test_main.py requirements.txt
git commit -m "feat: adiciona deteccao de objetos com yolo"
```

### Task 3: Ligar YOLO ao video e ao WebSocket

**Files:** `funcs.py`, `main.py`, `tests/test_main.py`

**Interfaces:** `trackVideo(img, previous_detections=None, detector=None) -> tuple[np.ndarray, list[dict]]`; `main.processVideo` mantem seu contrato atual.

- [ ] **Step 1: Write failing integration tests**

Injetar `FakeDetector` em `trackVideo` e verificar dois IDs `object-1` e `object-2`, classes preservadas e forma do frame. Criar `EmptyDetector` que retorna `[]` e verificar que o resultado tambem e `[]` sem excecao.

- [ ] **Step 2: Run and verify failure**

Run: `.venv/bin/python -m pytest tests/test_main.py -k "track_video or empty_detections" -q`

Expected: FAIL porque o tracking atual depende de limiarizacao e nao aceita detector injetado.

- [ ] **Step 3: Preserve IDs and metadata**

Fazer `trackVideo` chamar `detect_objects`, passar deteccoes a `match_detections` e preservar classe, confianca e caixa ao atribuir IDs por distancia dos centros. Instanciar um detector para o processo do servidor para nao recarregar pesos por frame.

- [ ] **Step 4: Preserve WebSocket payload**

Manter PNG binario e JSON `{"type":"detections","objects": [...]}`. Permitir que `processVideo` use o detector configurado sem mudar o protocolo do navegador.

- [ ] **Step 5: Validate syntax and tests**

Run: `.venv/bin/python -m py_compile funcs.py main.py && .venv/bin/python -m pytest tests/test_main.py -q`

Expected: PASS sem download porque os testes injetam detector falso.

- [ ] **Step 6: Commit**

```bash
git add funcs.py main.py tests/test_main.py
git commit -m "fix: conta deteccoes yolo em cada frame"
```

### Task 4: Validar instalacao e regressao

**Files:** `README.md` (criar); `tests/test_main.py` somente se a validacao revelar regressao.

- [ ] **Step 1: Install dependency**

Run: `.venv/bin/python -m pip install -r requirements.txt`

Expected: `ultralytics` importavel. Se o ambiente nao permitir instalacao, registrar o erro exato e manter os testes com detector falso executaveis.

- [ ] **Step 2: Run complete suite**

Run: `.venv/bin/python -m pytest -q`

Expected: todos os testes passam.

- [ ] **Step 3: Run measurement smoke test**

Executar um script com dois retangulos que chame `area`, `perimeter`, `diameter` e `objects`, verificando forma BGR e conclusao rapida.

- [ ] **Step 4: Document model setup**

Documentar `YOLO_MODEL_PATH`, nome padrao do peso, download na primeira execucao, limiar de confianca e limitacao ao vocabulario do modelo. Explicar que a contagem e por frame e que IDs servem apenas para continuidade e novos objetos.

- [ ] **Step 5: Review and commit**

Run: `git diff --check && git status --short`

```bash
git add README.md tests/test_main.py
git commit -m "test: valida fluxo completo de deteccao"
```