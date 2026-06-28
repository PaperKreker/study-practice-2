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
 * Выделяет жёлтым фоном слова из поискового запроса, а также термины,
 * которые подсветил бэкенд (учитывают морфологию русского языка —
 * например, разные падежи слова), найденные в тексте.
 *
 * @param {{ text: string, query: string, terms?: string[] }} props
 *   text  - отображаемый фрагмент текста
 *   query - поисковый запрос (разбивается на отдельные слова)
 *   terms - дополнительные термины для подсветки (из ответа бэкенда)
 */
function Highlight({ text, query, terms = [] }) {
  if (!text) {
    return <>{text}</>;
  }

  // Собираем все термины: слова запроса + подсвеченные бэкендом формы слов.
  const queryTerms = (query || '')
    .trim()
    .split(/\s+/)
    .filter((term) => term.length >= 1);
  const allTerms = [...queryTerms, ...terms.filter(Boolean)];

  // Убираем дубликаты без учёта регистра.
  const seen = new Set();
  const uniqueTerms = [];
  allTerms.forEach((term) => {
    const key = term.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      uniqueTerms.push(term);
    }
  });

  if (uniqueTerms.length === 0) {
    return <>{text}</>;
  }

  // Длинные термины раньше коротких — чтобы в альтернации выигрывало
  // самое длинное совпадение и не дробились более общие слова.
  uniqueTerms.sort((a, b) => b.length - a.length);
  const escaped = uniqueTerms.map(escapeRegExp);

  const splitRegex = new RegExp(`(${escaped.join('|')})`, 'gi');
  // Отдельное выражение без флага "g" для проверки — у глобального RegExp
  // состояние lastIndex меняется между вызовами test() и ломает результат.
  const matchRegex = new RegExp(`^(?:${escaped.join('|')})$`, 'i');
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
