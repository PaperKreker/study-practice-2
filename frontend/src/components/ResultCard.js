import React from 'react';
import Highlight from './Highlight';

/**
 * Извлекает термины, которые бэкенд обернул в теги <mark>...</mark>
 * в подсвеченных фрагментах. Это именно те формы слов, что нашёл поиск
 * (с учётом морфологии), поэтому их стоит подсветить во всём тексте.
 * @param {string[]} highlights - фрагменты с тегами <mark>
 * @returns {string[]} список уникальных найденных терминов
 */
function extractMarkedTerms(highlights) {
  if (!Array.isArray(highlights)) {
    return [];
  }
  const terms = new Set();
  const markRegex = /<mark>(.*?)<\/mark>/gi;
  highlights.forEach((fragment) => {
    if (typeof fragment !== 'string') {
      return;
    }
    let match = markRegex.exec(fragment);
    while (match !== null) {
      const term = match[1].trim();
      if (term) {
        terms.add(term);
      }
      match = markRegex.exec(fragment);
    }
  });
  return [...terms];
}

/**
 * Карточка результата поиска.
 * Содержит: название файла, номер страницы, найденный фрагмент текста с
 * подсветкой совпадений и оценку релевантности.
 *
 * @param {{ result: Object, query: string }} props
 *   result.file_name  - имя исходного файла
 *   result.page       - номер страницы
 *   result.text       - найденный фрагмент текста
 *   result.score      - оценка релевантности
 *   result.highlights - подсвеченные бэкендом фрагменты
 */
function ResultCard({ result, query }) {
  const { file_name: fileName, page, text, score, highlights } = result;

  // Термины, реально найденные поиском (включая словоформы из морфологии).
  const markedTerms = extractMarkedTerms(highlights);

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
        <Highlight text={text || ''} query={query} terms={markedTerms} />
      </p>
    </article>
  );
}

export default ResultCard;
