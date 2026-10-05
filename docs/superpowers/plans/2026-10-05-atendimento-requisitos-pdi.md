# Atendimento dos Requisitos de PDI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adequar o aplicativo às exigências de processamento de imagens e vídeo, padronizar os nomes das funções em português e identificar explicitamente os bônus já disponíveis.

**Architecture:** Preservar o servidor WebSocket em `main.py`, concentrar os algoritmos em `funcs.py` e manter `index.html` como interface. O servidor continuará recebendo imagens e quadros, aplicando uma cadeia de operações identificada por códigos, retornando PNGs e enviando eventos de áudio ao navegador quando o rastreamento detectar o objeto.

**Tech Stack:** Python 3, NumPy, OpenCV, Matplotlib, `websockets`, HTML, JavaScript e API de áudio do navegador.

## Global Constraints

- Usar nomes de funções em português e `snake_case`, conforme a especificação aprovada.
- Preservar a interface web e o protocolo WebSocket existente, acrescentando apenas mensagens de evento necessárias ao áudio.
- Não adicionar uma biblioteca Python de áudio; reproduzir a música no navegador com um arquivo local.
- Implementar rotulação de componentes conexos e associar área, perímetro e diâmetro a cada componente.
- Substituir exceções genéricas e silenciosas por validações e erros específicos.
- Marcar somente funcionalidades extras com comentários curtos `# BÔNUS:`.
- Validar com a `.venv` existente do projeto.

---

### Task 1: Renomear algoritmos e estabelecer testes básicos

**Files:**
- Modify: `funcs.py`
- Modify: `main.py`
- Create: `tests/test_processamento.py`

**Interfaces:**
- Produces `converter_para_niveis_de_cinza(img)`, `converter_para_negativo(img)`,
  `limiarizacao(img, limiar=0)`, `limiarizacao_otsu(img)`,
  `suavizacao_media(img, janela)`, `suavizacao_mediana(img, janela)`,
  `detectar_bordas_canny(img, limiar_inferior, limiar_superior)`,
  `erosao(img, tamanho_kernel)`, `dilatacao(img, tamanho_kernel)`,
  `abertura(img, tamanho_kernel)`, `fechamento(img, tamanho_kernel)`,
  `calcular_histograma(img, titulo='', normalizado=False, cumulativo=False, plotar=True)`.
- Produces video variants `suavizacao_media_video`, `suavizacao_mediana_video`,
  `calcular_area_video`, `calcular_perimetro_video`,
  `calcular_diametro_video`, `rotular_componentes_conexos_video` and
  `rastrear_objeto`.
- `main.py` maps protocol codes to these names without changing the numeric wire format.

- [ ] **Step 1: Write failing tests for conversions and filter names**

```python
import numpy as np

from funcs import (
    converter_para_niveis_de_cinza,
    converter_para_negativo,
    limiarizacao,
    limiarizacao_otsu,
)


def test_conversoes_basicas():
    imagem = np.array([[[30, 60, 90], [255, 255, 255]]], dtype=np.uint8)
    cinza = converter_para_niveis_de_cinza(imagem)
    assert cinza.shape == (1, 1)
    assert cinza.dtype == np.uint8
    np.testing.assert_array_equal(converter_para_negativo(np.array([[0, 255]], dtype=np.uint8)), [[255, 0]])


def test_limiarizacao_e_otsu_retornam_imagem_binaria():
    imagem = np.array([[0, 0, 255, 255]], dtype=np.uint8)
    assert set(np.unique(limiarizacao(imagem, 100))) == {0, 255}
    assert set(np.unique(limiarizacao_otsu(imagem))) == {0, 255}
```

- [ ] **Step 2: Run the focused tests and verify the old names fail**

Run: `.venv/bin/python -m pytest tests/test_processamento.py -q`

Expected: FAIL before the rename because the required Portuguese function names do not exist.

- [ ] **Step 3: Rename implementations and all internal references**

Use direct function definitions with the signatures above. Update the image and
video maps in `main.py`, calls from `processar_imagem`/`processar_video` and
the code that handles the histogram keyword arguments. Keep protocol codes
unchanged so the existing JavaScript client remains compatible.

- [ ] **Step 4: Add explicit bonus comments**

Add only these comments in `funcs.py`:

```python
# BÔNUS: permite limiarização manual além do método de Otsu exigido.
# BÔNUS: normaliza a faixa de intensidades da imagem.
# BÔNUS: oferece histograma cumulativo e normalizado.
# BÔNUS: implementação manual da suavização para imagens.
# BÔNUS: algoritmo KCF permitido como escolha de rastreamento.
```

Place each comment immediately above the corresponding function and do not
label mandatory algorithms as bonus.

- [ ] **Step 5: Run the focused tests**

Run: `.venv/bin/python -m pytest tests/test_processamento.py -q`

Expected: PASS, including import of every required function name.

- [ ] **Step 6: Commit the isolated rename**

```bash
git add funcs.py main.py tests/test_processamento.py
git commit -m "refactor: padroniza nomes dos algoritmos de PDI"
```

If Git is still unavailable in the workspace, leave the files changed and
record that the commit could not be created.

### Task 2: Implement unified component labeling and per-object measurements

**Files:**
- Modify: `funcs.py`
- Modify: `main.py`
- Modify: `tests/test_processamento.py`

**Interfaces:**
- Produces `rotular_componentes_conexos(imagem_binaria) -> tuple[np.ndarray, list[dict]]`.
- Each component dictionary contains `rotulo`, `pixels`, `area`, `perimetro`,
  `diametro` and `posicao_texto`.
- Produces annotation functions that render the component labels and requested
  measurements on a BGR image.

- [ ] **Step 1: Add a failing synthetic-component test**

```python
def test_rotula_dois_componentes_e_calcula_medidas_por_objeto():
    imagem = np.zeros((7, 10), dtype=np.uint8)
    imagem[1:3, 1:3] = 255
    imagem[4:6, 6:9] = 255

    rotulada, componentes = rotular_componentes_conexos(imagem)

    assert rotulada.max() == 2
    assert len(componentes) == 2
    assert sorted(c["area"] for c in componentes) == [4, 6]
    assert all(c["perimetro"] > 0 for c in componentes)
    assert all(c["diametro"] > 0 for c in componentes)
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `.venv/bin/python -m pytest tests/test_processamento.py::test_rotula_dois_componentes_e_calcula_medidas_por_objeto -q`

Expected: FAIL because the unified component-labeling interface is not present.

- [ ] **Step 3: Implement one traversal per component**

Use a queue or stack with 8-connectivity only if that choice is documented;
otherwise use the current 4-connectivity behavior consistently. Visit each
foreground pixel once, store its coordinates, compute area from pixel count,
compute perimeter from exposed 4-neighbor sides, and compute diameter as the
maximum Euclidean distance among the component border pixels. Use integer
labels starting at 1 and leave background as 0.

- [ ] **Step 4: Route object operations through the shared result**

Make `rotular_componentes_conexos`, `calcular_area`, `calcular_perimetro`,
`calcular_diametro` and object counting use the same component data so all
operations refer to identical objects. Return BGR annotation images for the
WebSocket response and preserve the current numeric filter codes.

- [ ] **Step 5: Run component tests**

Run: `.venv/bin/python -m pytest tests/test_processamento.py -q`

Expected: PASS with exactly two components and independent measurements.

- [ ] **Step 6: Commit the component implementation**

```bash
git add funcs.py main.py tests/test_processamento.py
git commit -m "feat: rotula componentes e mede objetos individualmente"
```

### Task 3: Correct image/video routing and explicit error handling

**Files:**
- Modify: `main.py`
- Modify: `funcs.py`
- Modify: `tests/test_processamento.py`

**Interfaces:**
- Produces `processar_imagem(imagem)` and `processar_video(imagem)`.
- A stream type of `1` always uses image processing; a stream type of `2`
  always uses video processing.
- Invalid decoded frames raise a clear `ValueError` before processing.

- [ ] **Step 1: Add tests for routing and invalid input**

```python
def test_processamento_rejeita_imagem_invalida():
    with pytest.raises(ValueError, match="imagem"):
        validar_imagem_decodificada(None)


def test_mapas_mantem_rastreamento_somente_no_video():
    assert mapa_funcoes_imagem[16] is processar_sem_alteracao
    assert mapa_funcoes_video[16] is rastrear_objeto
```

- [ ] **Step 2: Run the tests and verify the routing assertions fail**

Run: `.venv/bin/python -m pytest tests/test_processamento.py -q`

Expected: FAIL because the current code repeats the image stream condition and
uses generic names.

- [ ] **Step 3: Rename the processing entry points and fix the branch**

Replace the duplicated `streamType == 1` condition with the video branch for
`stream_type == 2`. Validate `cv2.imdecode` results before calling a pipeline.
Use targeted exceptions for malformed WebSocket payloads, invalid filter
parameters and tracker initialization.

- [ ] **Step 4: Remove silent catches**

Do not use bare `except`. Catch `ValueError`, `IndexError`, `cv2.error` and
other expected errors separately, log the operation and send an explicit
error message only if the WebSocket protocol has a defined error frame.
Never replace a failed result with a success-shaped image.

- [ ] **Step 5: Run syntax, imports and focused tests**

Run:

```bash
.venv/bin/python -m py_compile main.py funcs.py
.venv/bin/python -m pytest tests/test_processamento.py -q
```

Expected: both commands succeed.

- [ ] **Step 6: Commit the routing fix**

```bash
git add main.py funcs.py tests/test_processamento.py
git commit -m "fix: separa processamento de imagem e video"
```

### Task 4: Add browser audio alert for tracked-object detection

**Files:**
- Modify: `main.py`
- Modify: `funcs.py`
- Modify: `index.html`
- Modify: `README.md`
- Create: `assets/alerta.mp3`
- Modify: `tests/test_processamento.py`

**Interfaces:**
- `rastrear_objeto(imagem, rastreador) -> tuple[np.ndarray, bool]` returns the
  annotated frame and whether the tracker currently has a valid detection.
- The server sends a small text event `{"tipo":"alerta_objeto"}` only when the
  detection changes from false to true.
- The browser owns an `Audio` object and plays `assets/alerta.mp3` once per event.

- [ ] **Step 1: Add a failing tracker-event test**

```python
def test_rastreamento_informa_deteccao_valida():
    class Rastreador:
        def update(self, _imagem):
            return True, (1, 1, 3, 3)

    quadro, detectado = rastrear_objeto(np.zeros((8, 8, 3), dtype=np.uint8), Rastreador())
    assert quadro.shape == (8, 8, 3)
    assert detectado is True
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `.venv/bin/python -m pytest tests/test_processamento.py::test_rastreamento_informa_deteccao_valida -q`

Expected: FAIL because the current tracker function returns only an image.

- [ ] **Step 3: Return detection state and track the alert edge**

Update `rastrear_objeto` to return `(imagem_anotada, sucesso)`. In the
connection handler, keep `detecao_anterior` per client, send the JSON event
only when `sucesso and not detecao_anterior`, and reset the state when tracking
fails or the stream changes.

- [ ] **Step 4: Implement browser playback without a Python audio dependency**

Add an `Audio("assets/alerta.mp3")` object in `index.html`, handle incoming
string messages separately from binary PNG messages, and call `audio.play()`
for the alert event. Display a clear console error if playback is blocked by
browser autoplay policy. Document that the user may need to interact with the
page once before audio can play.

- [ ] **Step 5: Add the audio file and documentation**

Place a short, locally distributable MP3 at `assets/alerta.mp3`. Update
`README.md` with the required file path, browser permission behavior and the
fact that the alert is triggered on a successful tracking transition.

- [ ] **Step 6: Run tracker and syntax tests**

Run:

```bash
.venv/bin/python -m py_compile main.py funcs.py
.venv/bin/python -m pytest tests/test_processamento.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit the audio alert**

```bash
git add main.py funcs.py index.html README.md assets/alerta.mp3 tests/test_processamento.py
git commit -m "feat: alerta sonoro para objeto rastreado"
```

### Task 5: Verify the complete rubric and document bonus features

**Files:**
- Modify: `README.md`
- Modify: `tests/test_processamento.py`

- [ ] **Step 1: Add a protocol/map coverage test**

```python
def test_exigencias_tem_operacao_mapeada():
    nomes_obrigatorios = {
        "converter_para_niveis_de_cinza",
        "converter_para_negativo",
        "limiarizacao_otsu",
        "suavizacao_media",
        "suavizacao_mediana",
        "detectar_bordas_canny",
        "erosao",
        "dilatacao",
        "abertura",
        "fechamento",
        "calcular_histograma",
        "rotular_componentes_conexos",
        "calcular_area",
        "calcular_perimetro",
        "calcular_diametro",
        "rastrear_objeto",
    }
    assert nomes_obrigatorios <= nomes_exportados
```

- [ ] **Step 2: Run the complete local validation**

Run:

```bash
.venv/bin/python -m py_compile main.py funcs.py
.venv/bin/python -m pytest -q
```

Expected: all tests pass and both Python modules compile.

- [ ] **Step 3: Update the requirement matrix in README**

Document each item as implemented, partially implemented or pending, explain
that music requires `assets/alerta.mp3`, and list the bonuses with the same
names used by the `# BÔNUS:` comments.

- [ ] **Step 4: Perform a manual smoke test**

Run `.venv/bin/python main.py`, open `index.html`, upload a binary test image,
exercise each image operation, enable the camera, select tracking and confirm
that the PNG stream remains active and that the audio event is emitted on a
successful detection.

- [ ] **Step 5: Commit the final documentation and tests**

```bash
git add README.md tests/test_processamento.py
git commit -m "docs: registra atendimento da rubrica de PDI"
```

## Self-review

- **Spec coverage:** Tasks 1 and 5 cover the interface-visible operations and
  naming; Task 2 covers connected components and per-object metrics; Task 3
  covers image/video routing and error handling; Task 4 covers tracking and
  music; Task 5 covers documentation and final verification.
- **Placeholder scan:** No `TBD`, `TODO`, or unspecified implementation step is
  used in this plan.
- **Type consistency:** The tracker interface is explicitly changed to return
  `(np.ndarray, bool)` and the handler consumes both values; component
  functions use a labeled array and a list of dictionaries consistently.
