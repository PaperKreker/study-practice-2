import React, { useEffect, useRef, useState } from 'react';

/**
 * Поле ввода поискового запроса с кнопкой «Найти».
 * Поиск запускается по кнопке и по нажатию Enter.
 * Показывает выпадающий список истории запросов при фокусе.
 *
 * @param {{
 *   value: string,
 *   onChange: (value: string) => void,
 *   onSearch: (query: string) => void,
 *   loading?: boolean,
 *   history?: Array<{ id?: string, query: string, results_count?: number }>,
 *   onClearHistory?: () => void,
 * }} props
 */
function SearchBar({
  value,
  onChange,
  onSearch,
  loading,
  history = [],
  onClearHistory,
}) {
  const [showHistory, setShowHistory] = useState(false);
  const containerRef = useRef(null);

  // Закрываем выпадающий список при клике вне компонента.
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setShowHistory(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (event) => {
    event.preventDefault();
    setShowHistory(false);
    onSearch(value);
  };

  const handleHistoryClick = (query) => {
    onChange(query);
    setShowHistory(false);
    onSearch(query);
  };

  return (
    <div className="search-bar" ref={containerRef}>
      <form className="search-bar__form" onSubmit={handleSubmit} role="search">
        <input
          type="text"
          className="search-bar__input"
          placeholder="Введите поисковый запрос..."
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onFocus={() => setShowHistory(true)}
          aria-label="Поисковый запрос"
          autoComplete="off"
        />
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </form>

      {showHistory && history.length > 0 && (
        <ul className="search-history">
          <li className="search-history__header">
            <span>История запросов</span>
            {onClearHistory && (
              <button
                type="button"
                className="link-button"
                onClick={() => onClearHistory()}
              >
                Очистить
              </button>
            )}
          </li>
          {history.map((item) => (
            <li key={item.id || item.query}>
              <button
                type="button"
                className="search-history__item"
                onClick={() => handleHistoryClick(item.query)}
              >
                <span className="search-history__icon" aria-hidden="true">
                  🕘
                </span>
                <span className="search-history__query">{item.query}</span>
                {typeof item.results_count === 'number' && (
                  <span className="search-history__count">
                    {item.results_count}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SearchBar;
