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

export function formatFilterLabel(filter) {
  const values = filter.values || [];
  if (values.length === 0) return filter.name;
  return `${filter.name} ${'\u00b7'} ${values.join(' / ')}`;
}

export function toPayload(filters, getFilterId) {
  return [0, ...filters.flatMap(filter => [
    getFilterId(filter.name),
    filter.values?.[0] ?? 0,
    filter.values?.[1] ?? 0,
  ])];
}