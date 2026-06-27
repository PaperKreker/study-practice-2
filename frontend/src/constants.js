/**
 * Общие константы приложения.
 */

/** Состояния обработки загружаемого файла. */
export const UPLOAD_STATUS = {
  UPLOADING: 'uploading',
  INDEXING: 'indexing',
  DONE: 'done',
  ERROR: 'error',
};

/** Подписи состояний. */
export const STATUS_LABELS = {
  [UPLOAD_STATUS.UPLOADING]: 'Загрузка...',
  [UPLOAD_STATUS.INDEXING]: 'Индексация...',
  [UPLOAD_STATUS.DONE]: 'Готово',
  [UPLOAD_STATUS.ERROR]: 'Ошибка',
};

/**
 * Нормализует статус документа, пришедший с бэкенда, к одному из значений
 * UPLOAD_STATUS. Бэкенд может использовать разные термины.
 * @param {string} backendStatus - статус из ответа сервера
 * @returns {string} нормализованный статус
 */
export function normalizeStatus(backendStatus) {
  const value = (backendStatus || '').toLowerCase();
  if (['ready', 'indexed', 'done', 'completed', 'success'].includes(value)) {
    return UPLOAD_STATUS.DONE;
  }
  if (['error', 'failed', 'failure'].includes(value)) {
    return UPLOAD_STATUS.ERROR;
  }
  if (['indexing', 'processing', 'pending'].includes(value)) {
    return UPLOAD_STATUS.INDEXING;
  }
  return UPLOAD_STATUS.INDEXING;
}
