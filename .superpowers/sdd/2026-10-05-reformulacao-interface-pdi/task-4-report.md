# Task 4 report

Implemented connection, processing, error, disconnected, and empty states for the PDI interface.

- Added and tested `getViewerMessage` with the exact required messages.
- Added `setUiState` with `aria-busy`, safe filter disabling, connection labels, and viewer/status feedback.
- Synchronized busy state with dynamically rendered edit/remove controls in the active-filter rail and restored controls after failures.
- Kept loading and processing messages visible in the viewer overlay without replacing a valid image.
- Wired WebSocket lifecycle, file loading, camera startup, processing, PNG binary results, and text/JSON errors.
- Prevented filter actions without an image and avoided sending empty filter payloads without a client image.
- Preserved original-image restoration only when a client-side original image exists, without clearing the camera viewer when its last filter is removed.
- README unchanged because startup instructions and protocol did not change.

## Validation

- `node --test tests/ui-state.test.mjs`: 12 passing
- `python3 -m py_compile main.py funcs.py`: passed
- Inline module extracted from `index.html` and checked with `node --check`: passed
- `git diff --check`: passed

## Concerns

Browser-level WebSocket and camera integration was not exercised in this environment; server, algorithms, and binary protocol remain intentionally untouched.
