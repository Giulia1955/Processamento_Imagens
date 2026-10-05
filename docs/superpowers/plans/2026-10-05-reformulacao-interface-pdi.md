# Reformulacao da interface PDI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reformular a interface de processamento de imagens para notebooks, com hierarquia visual clara, filtros agrupados, estados explicitos e remocao acessivel por botao `X`.

**Architecture:** Manter o servidor WebSocket e o protocolo numerico existentes. Extrair o estado puro da cadeia de filtros para um modulo JavaScript testavel, usar `index.html` como camada de apresentacao e transporte, e renderizar a trilha inferior sempre a partir do estado atual para evitar indices obsoletos.

**Tech Stack:** HTML, CSS, JavaScript ES modules, Node.js test runner, Python 3, OpenCV, NumPy, WebSocket existente.

## Global Constraints

- Preservar o servidor Python, os mapas de filtros e o protocolo WebSocket numerico atual.
- Priorizar desktop/notebook; oferecer somente adaptacao basica para larguras menores.
- Usar a direcao visual aprovada: fundo grafite, superficies azul-esverdeadas, verde menta para acao e tipografia autoral.
- Cada filtro ativo deve possuir botao `X` visivel, acessivel por teclado e com `aria-label`.
- Remover um filtro deve reaplicar os demais na mesma ordem; remover o ultimo deve restaurar a imagem original.
- Todos os botoes devem ser elementos `button`, com foco visivel e estados de hover, ativo e desabilitado.
- Nao introduzir framework frontend, bundle ou dependencia adicional.
- Nao alterar algoritmos de processamento nem o formato das mensagens WebSocket.
- Usar ASCII nos arquivos novos e preservar alteracoes locais existentes que nao pertencam a esta tarefa.

---

## Mapa de arquivos

- **Create:** `ui-state.mjs` — estado puro da cadeia de filtros, remocao segura, formatacao e serializacao do payload.
- **Create:** `tests/ui-state.test.mjs` — testes Node.js para a cadeia de filtros e payload.
- **Modify:** `index.html` — estrutura semantica, estilos, controles agrupados, trilha de filtros, estados visuais e integracao com `ui-state.mjs`.
- **Modify:** `README.md` — documentar a nova forma de executar e usar a interface, se os comandos ou comportamento visivel mudarem.
- **Validate:** `main.py`, `funcs.py` — somente compilacao e testes de regressao; nao alterar salvo bloqueio diretamente causado pela interface.

---

### Task 1: Extrair estado testavel dos filtros

**Files:**
- Create: `ui-state.mjs`
- Create: `tests/ui-state.test.mjs`

**Interfaces:**
- Produces `createFilterState(initialFilters = []) -> { filters, addFilter, updateFilter, removeFilter, clearFilters, toPayload }`.
- Produces `formatFilterLabel(filter) -> string`.
- `filters` uses objects with `{ name: string, values: number[] }`.
- `toPayload(filters, getFilterId) -> number[]` returns `[0, id, p1, p2, ...]`, preserving order.

- [ ] **Step 1: Add a minimal Node test file**

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { createFilterState, formatFilterLabel, toPayload } from '../ui-state.mjs';

const ids = { Grayscale: 0, Canny: 5, Negative: 1 };

 test('removeFilter removes only the selected filter and preserves order', () => {
  const state = createFilterState([
    { name: 'Grayscale', values: [] },
    { name: 'Canny', values: [5, 50] },
    { name: 'Negative', values: [] },
  ]);

  state.removeFilter(1);

  assert.deepEqual(state.filters, [
    { name: 'Grayscale', values: [] },
    
    { name: 'Negative', values: [] },
  ]);
});

test('toPayload includes the protocol type and both parameters', () => {
  const state = createFilterState([{ name: 'Canny', values: [5, 50] }]);
  assert.deepEqual(toPayload(state.filters, name => ids[name]), [0, 5, 5, 50]);
});

test('formatFilterLabel displays parameters when present', () => {
  assert.equal(formatFilterLabel({ name: 'Canny', values: [5, 50] }), 'Canny · 5 / 50');
});
```

- [ ] **Step 2: Run the focused test and verify the expected failure**

Run: `node --test tests/ui-state.test.mjs`

Expected: FAIL because `ui-state.mjs` does not exist yet.

- [ ] **Step 3: Implement the smallest pure state module**

Create immutable-style operations that replace the `filters` array rather than
mutating DOM nodes. Guard `removeFilter` against an invalid index and return the
same logical state when the index is outside the array. Use this implementation
shape:

```js
export function createFilterState(initialFilters = []) {
  let filters = initialFilters.map(filter => ({
    name: filter.name,
    values: [...(filter.values || [])],
  }));

  return {
    get filters() { return filters; },
    addFilter(name, values = []) {
      filters = [...filters, { name, values: [...values] }];
    },
    updateFilter(index, name, values = []) {
      if (!filters[index]) return;
      filters = filters.map((filter, currentIndex) =>
        currentIndex === index ? { name, values: [...values] } : filter,
      );
    },
    removeFilter(index) {
      if (index < 0 || index >= filters.length) return;
      filters = filters.filter((_, currentIndex) => currentIndex !== index);
    },
    clearFilters() { filters = []; },
    toPayload(getFilterId) { return toPayload(filters, getFilterId); },
  };
}
```

Implement `formatFilterLabel` and `toPayload` beside it. `toPayload` must use
zero for absent parameters and skip no valid filter entries.

- [ ] **Step 4: Run the focused tests and verify they pass**

Run: `node --test tests/ui-state.test.mjs`

Expected: PASS for removal, order, label formatting and payload serialization.

- [ ] **Step 5: Add edge-case tests before moving on**

Add tests for removing index `0`, removing the last index, removing from an empty
state, clearing all filters, and serializing a filter with no values. Run the same
command and confirm all tests pass.

- [ ] **Step 6: Commit the isolated state module**

```bash
git add ui-state.mjs tests/ui-state.test.mjs
git commit -m "test: extrai estado testavel dos filtros"
```

---

### Task 2: Rebuild the semantic page structure and visual system

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes the state API from `ui-state.mjs` through `<script type="module">`.
- Produces semantic regions: header, source controls, image viewer, filter panel,
  active-filter rail and live status message.

- [ ] **Step 1: Replace the fixed outer layout with semantic regions**

Create a page structure equivalent to:

```html
<main class="app-shell">
  <header class="app-header">
    <div class="brand"><span class="brand-mark">PDI</span><h1>Image Workshop</h1></div>
    <div id="connectionStatus" role="status" aria-live="polite">Connecting</div>
    <div class="source-actions" aria-label="Image source">
      <button id="cameraToggle" type="button">Start camera</button>
      <button id="imageSelect" type="button">Load image</button>
    </div>
  </header>
  <section class="workspace" aria-label="Image processing workspace">
    <section class="viewer-panel" aria-label="Image viewer">
      <div id="viewerState" class="viewer-state">Load an image or start the camera</div>
      <img id="image" alt="Processed image preview">
    </section>
    <aside class="filter-panel" aria-label="Available filters">
      <div id="filterGroups"></div>
    </aside>
  </section>
  <section class="active-filters" aria-labelledby="activeFiltersTitle">
    <div class="section-heading"><h2 id="activeFiltersTitle">Applied filters</h2><span id="filterCount">0</span></div>
    <div id="filters" role="list" aria-live="polite"></div>
  </section>
  <p id="statusMessage" role="status" aria-live="polite"></p>
</main>
```

Keep the hidden file input and the existing canvas/video elements needed by the
WebSocket flow, but remove clickable `div` controls and the old fixed `80%/20%`
layout.

- [ ] **Step 2: Add CSS variables and the approved visual language**

Define variables for graphite background, dark teal surfaces, mint action,
soft text, muted text and coral error. Use CSS grid for the workspace, with the
viewer as the flexible column and the filter panel between `280px` and `360px`.
Use stable minimum dimensions for the viewer and buttons. Add visible `:focus-visible`
styles and avoid gradients, oversized hero typography and nested cards.

- [ ] **Step 3: Group filters by processing purpose**

Render filter buttons under these groups: `Basic adjustments`, `Edges and
smoothing`, `Morphology`, `Measurements`, and `Tracking`. Keep the existing
filter names and numeric mapping. Place parameter inputs in the same group as
their filter and use associated labels instead of placeholder-only fields.

- [ ] **Step 4: Add notebook-width safeguards**

Use a media query around `900px` to reduce panel width and allow the workspace
to stack only when the content would otherwise overlap. Keep the active-filter
rail horizontally scrollable. Verify long labels and parameter values wrap or
clip intentionally without changing control dimensions.

- [ ] **Step 5: Run syntax and existing Python regression checks**

Run:

```bash
python3 -m py_compile main.py funcs.py
```

Expected: PASS. Do not interpret visual changes as requiring backend changes.

- [ ] **Step 6: Commit the semantic visual foundation**

```bash
git add index.html
git commit -m "feat: reorganiza interface da ferramenta PDI"
```

---

### Task 3: Connect filter state, editing and X removal

**Files:**
- Modify: `index.html`
- Modify: `ui-state.mjs` only if a Task 1 test exposes a missing state operation.
- Test: `tests/ui-state.test.mjs`

**Interfaces:**
- `index.html` owns `const filterState = createFilterState()`.
- `renderActiveFilters()` renders every current filter from `filterState.filters`.
- `removeFilterAt(index)` removes by current render index, calls `sendFilters()` and updates the viewer.
- `sendFilters()` uses `filterState.toPayload(getFilterId)` and preserves the existing WebSocket payload.

- [ ] **Step 1: Add tests for removal edge cases**

Add these behaviors to `tests/ui-state.test.mjs`:

```js
test('removing the first item leaves middle and last items ordered', () => {
  const state = createFilterState([
    { name: 'Grayscale', values: [] },
    { name: 'Canny', values: [5, 50] },
    { name: 'Negative', values: [] },
  ]);
  state.removeFilter(0);
  assert.deepEqual(state.filters.map(filter => filter.name), ['Canny', 'Negative']);
});

test('clearing the last filter produces the empty payload', () => {
  const state = createFilterState([{ name: 'Negative', values: [] }]);
  state.removeFilter(0);
  assert.deepEqual(state.toPayload(ids), [0]);
});
```

- [ ] **Step 2: Run the tests and confirm the state contract**

Run: `node --test tests/ui-state.test.mjs`

Expected: PASS before wiring DOM behavior.

- [ ] **Step 3: Render active filters from current state**

Implement `renderActiveFilters()` to clear `#filters`, create one `li` or
`div[role="listitem"]` per filter, and append a text label plus a real button:

```js
function createRemoveButton(filter, index) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'filter-remove';
  button.textContent = 'X';
  button.title = `Remove ${filter.name}`;
  button.setAttribute('aria-label', `Remove filter ${filter.name}`);
  button.addEventListener('click', event => {
    event.stopPropagation();
    removeFilterAt(index);
  });
  return button;
}
```

The item body may reopen the existing parameter editor, but the remove button
must stop propagation and never open it. Do not preserve the old middle-click or
Shift removal behavior as the primary interaction.

- [ ] **Step 4: Rewire add, edit and send operations**

Make `addFilter(name, values)` update `filterState`, call `renderActiveFilters`
and then `sendFilters`. Make `sendFilters` send exactly the existing byte array
shape. When `filterState.filters.length === 0`, show `original image` if one is
loaded and show the empty-state message otherwise.

- [ ] **Step 5: Run focused and Python checks**

Run:

```bash
node --test tests/ui-state.test.mjs
python3 -m py_compile main.py funcs.py
```

Expected: all Node tests pass and Python compilation succeeds.

- [ ] **Step 6: Commit filter interaction behavior**

```bash
git add index.html ui-state.mjs tests/ui-state.test.mjs
git commit -m "feat: adiciona remocao acessivel de filtros"
```

---

### Task 4: Add connection, processing, error and empty states

**Files:**
- Modify: `index.html`
- Modify: `README.md` if user-visible behavior or startup instructions change.

**Interfaces:**
- Produces `setUiState(state, message = '')` with states `connecting`,
  `ready`, `loading`, `processing`, `result`, `error` and `disconnected`.
- Existing binary PNG handling remains separate from text/JSON error handling.

- [ ] **Step 1: Add a small state transition test surface**

Add a pure helper in `ui-state.mjs` if needed:

```js
export function getViewerMessage(state) {
  return {
    connecting: 'Connecting to processor',
    ready: 'Load an image or start the camera',
    loading: 'Loading image',
    processing: 'Applying filters',
    result: '',
    error: 'Something went wrong',
    disconnected: 'Processor unavailable',
  }[state] || '';
}
```

Test each returned message with Node's test runner before using it in the DOM.

- [ ] **Step 2: Wire WebSocket lifecycle states**

Set `connecting` before opening the socket, `ready` on open, `result` after a
binary image response, `disconnected` on close and `error` for transport or
processing failures. Keep `aria-live` messages concise and avoid replacing the
image with an error string.

- [ ] **Step 3: Add processing feedback and disabled states**

When a file or video frame is being sent, set `loading` or `processing` and add
`aria-busy="true"` to the viewer. Disable only actions that cannot safely run
while the relevant request is active. Ensure camera controls recover after an
error.

- [ ] **Step 4: Validate invalid input and no-image actions**

Prevent filter actions when no image has been loaded, set an actionable status
message, and do not send malformed payloads. Check that empty filters restore
the original image only when `originalImg` exists on the client.

- [ ] **Step 5: Run automated checks**

Run:

```bash
node --test tests/ui-state.test.mjs
python3 -m py_compile main.py funcs.py
```

Expected: PASS with no syntax errors.

- [ ] **Step 6: Commit the state feedback**

```bash
git add index.html ui-state.mjs tests/ui-state.test.mjs README.md
git commit -m "feat: comunica estados da interface PDI"
```

---

### Task 5: Browser validation, accessibility pass and documentation

**Files:**
- Modify: `index.html`
- Modify: `README.md`
- Test: `tests/ui-state.test.mjs`

- [ ] **Step 1: Run the complete automated validation**

Run:

```bash
node --test tests/ui-state.test.mjs
python3 -m py_compile main.py funcs.py
```

Expected: both commands pass.

- [ ] **Step 2: Start the existing WebSocket server and serve the page**

Run: `python3 main.py`

Open `index.html` in a browser through the existing local workflow and confirm
the WebSocket connects. Do not change the server port or protocol.

- [ ] **Step 3: Validate the primary desktop flow manually**

Use a notebook-sized viewport and verify:

1. The page opens in the approved editorial visual direction.
2. Empty state clearly offers image upload or camera start.
3. A loaded image remains contained and visually dominant.
4. Filter groups are scannable and parameter inputs are labeled.
5. A chain of at least four filters appears in the lower rail.
6. Clicking the `X` on the first, middle and last items removes only that item.
7. Removing all items restores the original image.
8. Clicking the item body edits it while clicking `X` does not open the editor.
9. Connection, loading, processing, result and error states are visible when triggered.

- [ ] **Step 4: Validate keyboard and smaller notebook width**

Tab through all controls, activate filters and `X` buttons with Enter/Space,
confirm visible focus, and inspect a narrower notebook viewport. Confirm no
text overlap, clipped essential labels or inaccessible controls.

- [ ] **Step 5: Update README with the final interaction model**

Document that filters are managed in the lower `Applied filters` rail and that
each active filter can be removed with its `X` button. Keep startup instructions
accurate and mention the existing Python and browser requirements only.

- [ ] **Step 6: Review the final diff without reverting unrelated work**

Run:

```bash
git diff --check HEAD~5..HEAD
git status --short
```

Confirm only planned files from this feature are committed and leave unrelated
pre-existing modifications untouched.

- [ ] **Step 7: Commit final documentation and polish**

```bash
git add index.html README.md tests/ui-state.test.mjs ui-state.mjs
git commit -m "docs: atualiza uso da nova interface PDI"
```

---

## Self-review against the approved SPEC

- Visual direction, palette, typography and notebook density: Task 2.
- Semantic hierarchy and grouped filters: Task 2.
- Visible `X`, safe current-index removal and order preservation: Tasks 1 and 3.
- Parameter labels, editor separation and empty-filter restoration: Task 3.
- Connection, loading, processing, result, error and empty states: Task 4.
- Keyboard, focus, labels, `aria-live` and real buttons: Tasks 2, 3 and 5.
- Notebook responsiveness and horizontal active-filter rail: Task 2 and Task 5.
- WebSocket compatibility and Python regression checks: Tasks 3, 4 and 5.
- Documentation and acceptance walkthrough: Task 5.

No task changes the Python processing algorithms or numeric WebSocket protocol.
