/**
 * Клиентская валидация загружаемых файлов.
 * Дублирует серверную проверку, чтобы дать пользователю мгновенную
 * обратную связь до отправки файла на сервер.
 */
import {
  ALLOWED_MIME_TYPES,
  ALLOWED_EXTENSIONS,
  MAX_FILE_SIZE,
} from '../config';
import { formatFileSize } from './format';

/**
 * Проверяет один файл на соответствие формату и размеру.
 * @param {File} file - проверяемый файл
 * @returns {string|null} текст ошибки или null, если файл корректен
 */
export function validateFile(file) {
  const lowerName = file.name.toLowerCase();
  const hasAllowedExt = ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
  const hasAllowedMime = ALLOWED_MIME_TYPES.includes(file.type);

  // Браузеры не всегда корректно определяют MIME для .docx, поэтому
  // достаточно совпадения либо по MIME, либо по расширению.
  if (!hasAllowedMime && !hasAllowedExt) {
    return 'Недопустимый формат. Разрешены только PDF и DOCX.';
  }
  if (file.size > MAX_FILE_SIZE) {
    return `Файл слишком большой (${formatFileSize(file.size)}). Максимум 20 МБ.`;
  }
  return null;
}
