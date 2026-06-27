import React from 'react';
import Highlight from './Highlight';

/**
 * Карточка результата поиска.
 * Содержит: название файла, номер страницы, найденный фрагмент текста с
 * подсветкой совпадений и оценку релевантности.
 *
 * @param {{ result: Object, query: string }} props
 *   result.file_name - имя исходного файла
 *   result.page      - номер страницы
 *   result.text      - найденный фрагмент текста
 *   result.score     - оценка релевантности
 */
function ResultCard({ result, query }) {
  const { file_name: fileName, page, text, score } = result;

  // Оценка релевантности может прийти как число — округляем для вывода.
  const formattedScore =
    typeof score === 'number' ? score.toFixed(2) : score || '—';

  return (
    <article className="result-card">
      <header className="result-card__header">
        <span className="result-card__file" title={fileName}>
          <span className="result-card__icon" aria-hidden="true">
          </span>
          {fileName || 'Без названия'}
        </span>
        <span className="result-card__score" title="Оценка релевантности">
          {formattedScore}
        </span>
      </header>

      {(page || page === 0) && (
        <div className="result-card__meta">Страница {page}</div>
      )}

      <p className="result-card__text">
        <Highlight text={text || ''} query={query} />
      </p>
    </article>
  );
}

export default ResultCard;
