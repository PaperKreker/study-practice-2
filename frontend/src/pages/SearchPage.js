import React, { useCallback, useEffect, useState } from 'react';
import SearchBar from '../components/SearchBar';
import ResultCard from '../components/ResultCard';
import Pagination from '../components/Pagination';
import {
  searchDocuments,
  fetchSearchHistory,
  clearSearchHistory,
} from '../services/api';
import { PAGE_SIZE } from '../config';
import { useAuth } from '../context/AuthContext';

/**
 * Страница поиска по документам.
 * Содержит поле поиска, карточки результатов с подсветкой,
 * пагинацию и сообщение о пустой выдаче.
 *
 * История поиска хранится на бэкенде и привязана к пользователю, поэтому
 * доступна только после входа в систему.
 */
function SearchPage() {
  const { user, token, isAuthenticated } = useAuth();

  const [query, setQuery] = useState('');
  // Запрос, по которому реально выполнен поиск (для подсветки и пагинации).
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [history, setHistory] = useState([]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  /** Загружает историю поиска текущего пользователя с сервера. */
  const loadHistory = useCallback(async () => {
    if (!isAuthenticated || !user) {
      setHistory([]);
      return;
    }
    try {
      const { items } = await fetchSearchHistory(user.id, token);
      setHistory(items);
    } catch (err) {
      // Историю показываем по возможности — её недоступность не критична.
      setHistory([]);
    }
  }, [isAuthenticated, user, token]);

  // Загружаем историю при входе пользователя и сбрасываем при выходе.
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  /** Выполняет запрос к API для конкретной страницы выдачи. */
  const runSearch = useCallback(
    async (searchQuery, targetPage) => {
      setLoading(true);
      setError(null);
      try {
        const { results: items, total: totalCount } = await searchDocuments(
          searchQuery,
          targetPage,
          PAGE_SIZE,
          token
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
    },
    [token]
  );

  /** Обработчик нового поиска (по кнопке/Enter/клику в истории). */
  const handleSearch = useCallback(
    async (rawQuery) => {
      const trimmed = (rawQuery || '').trim();
      if (!trimmed) {
        return;
      }
      setSubmittedQuery(trimmed);
      await runSearch(trimmed, 1);
      // Бэкенд сохраняет запрос в истории — перечитываем её для актуальности.
      loadHistory();
    },
    [runSearch, loadHistory]
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

  /** Очищает историю поиска пользователя на сервере. */
  const handleClearHistory = useCallback(async () => {
    if (!isAuthenticated || !user) {
      return;
    }
    try {
      await clearSearchHistory(user.id, token);
      setHistory([]);
    } catch (err) {
      // Ошибку очистки игнорируем — состояние истории не меняем.
    }
  }, [isAuthenticated, user, token]);

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

      {hasSearched && !loading && !error && total > 0 && (
        <p className="results-summary">Найдено совпадений: {total}</p>
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
