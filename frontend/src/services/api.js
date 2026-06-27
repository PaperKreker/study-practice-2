/**
 * Сервисный слой для взаимодействия с REST API бэкенда.
 *
 * Контракт API (согласуется с бэкенд-командой):
 *   POST /api/v1/documents/upload  — загрузка файла (multipart, поле "file")
 *   GET  /api/v1/documents         — список загруженных документов
 *   GET  /api/v1/documents/{id}    — статус конкретного документа (для опроса индексации)
 *   GET  /api/v1/search?q=&page=&size= — полнотекстовый поиск
 */
import { API_BASE_URL, PAGE_SIZE } from '../config';

/** Собирает абсолютный URL из базового адреса и пути. */
function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}

/**
 * Извлекает человекочитаемое сообщение об ошибке из ответа сервера.
 * @param {Response} response - объект ответа fetch
 * @returns {Promise<string>} текст ошибки
 */
async function extractErrorMessage(response) {
  try {
    const data = await response.json();
    // FastAPI обычно кладёт описание в поле detail
    if (data && data.detail) {
      return typeof data.detail === 'string'
        ? data.detail
        : JSON.stringify(data.detail);
    }
    if (data && data.message) {
      return data.message;
    }
  } catch (e) {
    // тело не является JSON — игнорируем
  }
  return `Ошибка сервера (${response.status})`;
}

/**
 * Загружает один файл на сервер с отслеживанием прогресса загрузки.
 * Используется XMLHttpRequest, так как fetch не умеет отдавать прогресс upload.
 *
 * @param {File} file - загружаемый файл
 * @param {(percent: number) => void} onProgress - колбэк прогресса (0..100)
 * @returns {Promise<Object>} данные созданного документа { id, file_name, status, ... }
 */
export function uploadDocument(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.open('POST', buildUrl('/api/v1/documents/upload'));

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && typeof onProgress === 'function') {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(xhr.responseText ? JSON.parse(xhr.responseText) : {});
        } catch (e) {
          resolve({});
        }
      } else {
        let message = `Ошибка загрузки (${xhr.status})`;
        try {
          const data = JSON.parse(xhr.responseText);
          if (data && data.detail) {
            message = typeof data.detail === 'string'
              ? data.detail
              : JSON.stringify(data.detail);
          }
        } catch (e) {
          // тело не JSON — оставляем общее сообщение
        }
        reject(new Error(message));
      }
    };

    xhr.onerror = () => reject(new Error('Не удалось соединиться с сервером'));
    xhr.send(formData);
  });
}

/**
 * Возвращает список всех загруженных документов.
 * @returns {Promise<Array>} массив документов
 */
export async function fetchDocuments() {
  const response = await fetch(buildUrl('/api/v1/documents'));
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = await response.json();
  // Поддерживаем как { documents: [...] }, так и просто [...]
  return Array.isArray(data) ? data : data.items || [];
}

/**
 * Возвращает статус одного документа по идентификатору.
 * Используется для опроса состояния индексации.
 * @param {string} id - идентификатор документа
 * @returns {Promise<Object>} документ со статусом
 */
export async function fetchDocumentStatus(id) {
  const response = await fetch(buildUrl(`/api/v1/documents/${id}`));
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  return response.json();
}

/**
 * Выполняет полнотекстовый поиск по документам.
 *
 * @param {string} query - поисковый запрос
 * @param {number} page - номер страницы (с 1)
 * @param {number} size - размер страницы
 * @returns {Promise<{ results: Array, total: number }>} результаты и общее число совпадений
 */
export async function searchDocuments(query, page = 1, size = PAGE_SIZE) {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    size: String(size),
  });
  const response = await fetch(buildUrl(`/api/v1/search?${params.toString()}`));
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = await response.json();

  // Нормализуем ответ: бэкенд может вернуть { results, total } или просто массив.
  if (Array.isArray(data)) {
    return { results: data, total: data.length };
  }
  const results = data.items || data.results || data.hits || [];
  const total = typeof data.total === 'number' ? data.total : results.length;
  return { results, total };
}
