import React from 'react';

/**
 * Формирует компактный список номеров страниц с многоточиями.
 * Например: 1 ... 4 5 [6] 7 8 ... 20
 * @param {number} current - текущая страница
 * @param {number} total - всего страниц
 * @returns {Array<number|string>} элементы для отрисовки
 */
function buildPageItems(current, total) {
  const items = [];
  const pushRange = (from, to) => {
    for (let i = from; i <= to; i += 1) items.push(i);
  };

  if (total <= 7) {
    pushRange(1, total);
    return items;
  }

  items.push(1);
  if (current > 4) items.push('…');

  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);
  pushRange(start, end);

  if (current < total - 3) items.push('…');
  items.push(total);
  return items;
}

/**
 * Постраничная навигация по результатам поиска.
 *
 * @param {{ page: number, totalPages: number, onPageChange: (page: number) => void }} props
 */
function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) {
    return null;
  }

  const items = buildPageItems(page, totalPages);

  return (
    <nav className="pagination" aria-label="Навигация по страницам">
      <button
        type="button"
        className="pagination__btn"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Предыдущая страница"
      >
        ‹
      </button>

      {items.map((item, index) =>
        item === '…' ? (
          <span key={`gap-${index}`} className="pagination__gap">
            …
          </span>
        ) : (
          <button
            type="button"
            key={item}
            className={`pagination__btn${
              item === page ? ' pagination__btn--active' : ''
            }`}
            onClick={() => onPageChange(item)}
            aria-current={item === page ? 'page' : undefined}
          >
            {item}
          </button>
        )
      )}

      <button
        type="button"
        className="pagination__btn"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="Следующая страница"
      >
        ›
      </button>
    </nav>
  );
}

export default Pagination;
