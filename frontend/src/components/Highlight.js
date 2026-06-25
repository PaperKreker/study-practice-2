import React from 'react';

/**
 * Экранирует спецсимволы регулярных выражений в строке.
 * @param {string} str - исходная строка
 * @returns {string} безопасная для RegExp строка
 */
function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Компонент подсветки совпадений.
 * Выделяет жёлтым фоном все слова из поискового запроса, найденные в тексте.
 *
 * @param {{ text: string, query: string }} props
 *   text  - отображаемый фрагмент текста
 *   query - поисковый запрос (разбивается на отдельные слова)
 */
function Highlight({ text, query }) {
  if (!query || !text) {
    return <>{text}</>;
  }

  // Разбиваем запрос на отдельные слова длиной от 2 символов и строим
  // объединённое регулярное выражение для подсветки каждого из них.
  const terms = query
    .trim()
    .split(/\s+/)
    .filter((term) => term.length >= 2)
    .map(escapeRegExp);

  if (terms.length === 0) {
    return <>{text}</>;
  }

  const splitRegex = new RegExp(`(${terms.join('|')})`, 'gi');
  // Отдельное выражение без флага "g" для проверки — у глобального RegExp
  // состояние lastIndex меняется между вызовами test() и ломает результат.
  const matchRegex = new RegExp(`^(?:${terms.join('|')})$`, 'i');
  const parts = text.split(splitRegex);

  return (
    <>
      {parts.map((part, index) =>
        matchRegex.test(part) ? (
          <mark key={index} className="highlight">
            {part}
          </mark>
        ) : (
          <React.Fragment key={index}>{part}</React.Fragment>
        )
      )}
    </>
  );
}

export default Highlight;
