export function createFilterState(initialFilters = []) {
  let filters = initialFilters.map(filter => ({
    name: filter.name,
    values: [...(filter.values || [])],
  }));

  return {
    get filters() {
      return filters.map(filter => ({
        name: filter.name,
        values: [...filter.values],
      }));
    },
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

export function formatFilterLabel(filter) {
  const values = filter.values || [];
  if (values.length === 0) return filter.name;
  return `${filter.name} ${'\u00b7'} ${values.join(' / ')}`;
}

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

export function shouldShowProcessingFeedback(sourceType) {
  return sourceType !== 2;
}

export function getNewDetectionIds(previousIds, currentObjects) {
  const previous = new Set(previousIds);
  return currentObjects
    .map(object => object.id)
    .filter(id => id && !previous.has(id));
}

export function toPayload(filters, getFilterId) {
  return [0, ...filters.flatMap(filter => [
    getFilterId(filter.name),
    filter.values?.[0] ?? 0,
    filter.values?.[1] ?? 0,
  ])];
}