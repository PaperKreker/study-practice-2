/**
 * Вспомогательные функции форматирования данных для отображения.
 */

/**
 * Форматирует размер файла в человекочитаемый вид.
 * @param {number} bytes - размер в байтах
 * @returns {string} например "1.4 МБ"
 */
export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '';
  const units = ['Б', 'КБ', 'МБ', 'ГБ'];
  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  const rounded = unitIndex === 0 ? value : value.toFixed(1);
  return `${rounded} ${units[unitIndex]}`;
}

/**
 * Форматирует дату загрузки в локальный вид (дата + время).
 * @param {string|number|Date} value - дата в любом распознаваемом формате
 * @returns {string} отформатированная строка или "—"
 */
export function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
