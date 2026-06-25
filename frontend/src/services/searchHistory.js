/**
 * Хранение истории поисковых запросов в localStorage.
 *
 * История хранится локально в браузере пользователя.
 */
const STORAGE_KEY = 'search_history';
const MAX_ITEMS = 10;

/**
 * Возвращает список последних поисковых запросов (от свежих к старым).
 * @returns {string[]} массив запросов
 */
export function getSearchHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

/**
 * Добавляет запрос в историю, убирая дубликаты и ограничивая длину списка.
 * @param {string} query - поисковый запрос
 * @returns {string[]} обновлённый список запросов
 */
export function addSearchHistory(query) {
  const trimmed = (query || '').trim();
  if (!trimmed) {
    return getSearchHistory();
  }
  const history = getSearchHistory().filter(
    (item) => item.toLowerCase() !== trimmed.toLowerCase()
  );
  history.unshift(trimmed);
  const limited = history.slice(0, MAX_ITEMS);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(limited));
  } catch (e) {
    // приватный режим / переполнение — молча игнорируем
  }
  return limited;
}

/**
 * Полностью очищает историю поиска.
 * @returns {string[]} пустой список
 */
export function clearSearchHistory() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    // игнорируем
  }
  return [];
}
