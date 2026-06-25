import React, { useCallback, useState } from 'react';
import SearchBar from '../components/SearchBar';
import ResultCard from '../components/ResultCard';
import Pagination from '../components/Pagination';
import { searchDocuments } from '../services/api';
import { PAGE_SIZE } from '../config';
import {
  getSearchHistory,
  addSearchHistory,
  clearSearchHistory,
} from '../services/searchHistory';

/**
 * Страница поиска по документам.
 * Содержит поле поиска, карточки результатов с подсветкой,
 * пагинацию и сообщение о пустой выдаче.
 */
function SearchPage() {
  const [query, setQuery] = useState('');
  // Запрос, по которому реально выполнен поиск (для подсветки и пагинации).
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [history, setHistory] = useState(() => getSearchHistory());

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  /** Выполняет запрос к API для конкретной страницы выдачи. */
  const runSearch = useCallback(async (searchQuery, targetPage) => {
    setLoading(true);
    setError(null);
    try {
      const { results: items, total: totalCount } = await searchDocuments(
        searchQuery,
        targetPage
      );
      setResults(items);
      setTotal(totalCount);
      setPage(targetPage);
    } catch (err) {
      setError(err.message || 'Не удалось выполнить поиск');
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
      setHasSearched(true);
    }
  }, []);

  /** Обработчик нового поиска (по кнопке/Enter/клику в истории). */
  const handleSearch = useCallback(
    (rawQuery) => {
      const trimmed = (rawQuery || '').trim();
      if (!trimmed) {
        return;
      }
      setSubmittedQuery(trimmed);
      setHistory(addSearchHistory(trimmed));
      runSearch(trimmed, 1);
    },
    [runSearch]
  );

  /** Переход на другую страницу выдачи. */
  const handlePageChange = useCallback(
    (targetPage) => {
      if (targetPage < 1 || targetPage > totalPages || targetPage === page) {
        return;
      }
      runSearch(submittedQuery, targetPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    [runSearch, submittedQuery, totalPages, page]
  );

  const handleClearHistory = useCallback(() => {
    setHistory(clearSearchHistory());
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Поиск по базе знаний</h1>
      <p className="page-subtitle">
        Введите запрос — система найдёт релевантные фрагменты в загруженных
        документах.
      </p>

      <SearchBar
        value={query}
        onChange={setQuery}
        onSearch={handleSearch}
        loading={loading}
        history={history}
        onClearHistory={handleClearHistory}
      />

      {error && <p className="error-text search-error">{error}</p>}

      {hasSearched && !loading && !error && (
        <p className="results-summary">
          {total > 0
            ? `Найдено совпадений: ${total}`
            : null}
        </p>
      )}

      {loading && <p className="muted-text">Идёт поиск...</p>}

      {/* Сообщение об отсутствии результатов */}
      {hasSearched && !loading && !error && results.length === 0 && (
        <div className="empty-state">
          <div className="empty-state__icon" aria-hidden="true">
            🔍
          </div>
          <p>
            По вашему запросу ничего не найдено. Попробуйте изменить
            формулировку
          </p>
        </div>
      )}

      {results.length > 0 && (
        <div className="results-list">
          {results.map((result, index) => (
            <ResultCard
              key={result.chunk_id || `${result.file_name}-${index}`}
              result={result}
              query={submittedQuery}
            />
          ))}
        </div>
      )}

      {!loading && results.length > 0 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}

export default SearchPage;
