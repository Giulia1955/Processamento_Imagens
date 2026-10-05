import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createFilterState,
  formatFilterLabel,
  getViewerMessage,
  getNewDetectionIds,
  shouldShowProcessingFeedback,
  toPayload,
} from '../ui-state.mjs';

const ids = { Grayscale: 0, Canny: 5, Negative: 1 };

test('getViewerMessage returns the exact message for each viewer state', () => {
  assert.deepEqual(
    ['connecting', 'ready', 'loading', 'processing', 'result', 'error', 'disconnected']
      .map(state => [state, getViewerMessage(state)]),
    [
      ['connecting', 'Connecting to processor'],
      ['ready', 'Load an image or start the camera'],
      ['loading', 'Loading image'],
      ['processing', 'Applying filters'],
      ['result', ''],
      ['error', 'Something went wrong'],
      ['disconnected', 'Processor unavailable'],
    ],
  );
  assert.equal(getViewerMessage('unknown'), '');
});

test('continuous camera frames do not show transient processing feedback', () => {
  assert.equal(shouldShowProcessingFeedback(1), true);
  assert.equal(shouldShowProcessingFeedback(2), false);
});

test('new detection ids exclude objects already present', () => {
  assert.deepEqual(
    getNewDetectionIds(['object-1'], [{ id: 'object-1' }, { id: 'object-2' }]),
    ['object-2'],
  );
});

test('an object is new again after the detection list becomes empty', () => {
  assert.deepEqual(getNewDetectionIds([], [{ id: 'object-1' }]), ['object-1']);
});

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
  assert.equal(
    formatFilterLabel({ name: 'Canny', values: [5, 50] }),
    `Canny ${'\u00b7'} 5 / 50`,
  );
});

test('removeFilter removes the first filter', () => {
  const state = createFilterState([
    { name: 'Grayscale', values: [] },
    { name: 'Negative', values: [] },
  ]);

  state.removeFilter(0);

  assert.deepEqual(state.filters, [{ name: 'Negative', values: [] }]);
});

test('removing the first item leaves middle and last items ordered', () => {
  const state = createFilterState([
    { name: 'Grayscale', values: [] },
    { name: 'Canny', values: [5, 50] },
    { name: 'Negative', values: [] },
  ]);

  state.removeFilter(0);

  assert.deepEqual(state.filters.map(filter => filter.name), ['Canny', 'Negative']);
});

test('removeFilter removes the last filter', () => {
  const state = createFilterState([
    { name: 'Grayscale', values: [] },
    { name: 'Negative', values: [] },
  ]);

  state.removeFilter(1);

  assert.deepEqual(state.filters, [{ name: 'Grayscale', values: [] }]);
});

test('removeFilter does nothing for an empty state', () => {
  const state = createFilterState();

  state.removeFilter(0);

  assert.deepEqual(state.filters, []);
});

test('clearFilters removes every filter', () => {
  const state = createFilterState([
    { name: 'Grayscale', values: [] },
    { name: 'Negative', values: [] },
  ]);

  state.clearFilters();

  assert.deepEqual(state.filters, []);
});

test('toPayload fills absent parameters with zero', () => {
  const state = createFilterState([{ name: 'Negative', values: [] }]);

  assert.deepEqual(toPayload(state.filters, name => ids[name]), [0, 1, 0, 0]);
});

test('clearing the last filter produces the empty payload', () => {
  const state = createFilterState([{ name: 'Negative', values: [] }]);

  state.removeFilter(0);

  assert.deepEqual(state.toPayload(ids), [0]);
});

test('filters getter prevents external mutation of state', () => {
  const state = createFilterState([{ name: 'Canny', values: [5, 50] }]);
  const snapshot = state.filters;

  snapshot.push({ name: 'Negative', values: [] });
  snapshot[0].name = 'Negative';
  snapshot[0].values[0] = 99;
  snapshot[0].values.push(100);

  assert.deepEqual(state.filters, [{ name: 'Canny', values: [5, 50] }]);
  assert.deepEqual(state.toPayload(name => ids[name]), [0, 5, 5, 50]);
});