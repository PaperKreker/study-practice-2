import {
  addSearchHistory,
  clearSearchHistory,
  getSearchHistory,
} from './searchHistory';

beforeEach(() => {
  localStorage.clear();
});

test('getSearchHistory returns an empty list for missing or invalid data', () => {
  expect(getSearchHistory()).toEqual([]);

  localStorage.setItem('search_history', '{broken');

  expect(getSearchHistory()).toEqual([]);
});

test('addSearchHistory trims, deduplicates, and stores newest queries first', () => {
  expect(addSearchHistory(' elastic ')).toEqual(['elastic']);
  expect(addSearchHistory('docs')).toEqual(['docs', 'elastic']);
  expect(addSearchHistory('ELASTIC')).toEqual(['ELASTIC', 'docs']);
  expect(getSearchHistory()).toEqual(['ELASTIC', 'docs']);
});

test('addSearchHistory keeps only ten latest queries', () => {
  for (let index = 0; index < 12; index += 1) {
    addSearchHistory(`query-${index}`);
  }

  const history = getSearchHistory();

  expect(history).toHaveLength(10);
  expect(history[0]).toBe('query-11');
  expect(history[9]).toBe('query-2');
});

test('clearSearchHistory removes stored queries', () => {
  addSearchHistory('elastic');

  expect(clearSearchHistory()).toEqual([]);
  expect(getSearchHistory()).toEqual([]);
});
