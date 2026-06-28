/**
 * Сервисный слой для взаимодействия с REST API бэкенда.
 *
 * Контракт API:
 *   POST   /api/v1/documents/upload          — загрузка файла (multipart, поле "file")
 *   GET    /api/v1/documents                 — список загруженных документов
 *   GET    /api/v1/documents/{id}            — статус конкретного документа
 *   GET    /api/v1/search?q=&page=&size=     — полнотекстовый поиск
 *   GET    /api/v1/search/history/{user_id}  — история поисковых запросов пользователя
 *   DELETE /api/v1/search/history/{user_id}  — очистка истории пользователя
 */
import { PAGE_SIZE } from '../config';
import { buildUrl, authHeaders, extractErrorMessage } from './http';

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
  // Поддерживаем как { items: [...] }, так и просто [...]
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
 * Если передан токен, он отправляется в заголовке — тогда бэкенд связывает
 * запрос с пользователем и сохраняет его в истории поиска.
 *
 * @param {string} query - поисковый запрос
 * @param {number} page - номер страницы (с 1)
 * @param {number} size - размер страницы
 * @param {string|null} token - токен доступа (необязательно)
 * @returns {Promise<{ results: Array, total: number }>} результаты и общее число совпадений
 */
export async function searchDocuments(query, page = 1, size = PAGE_SIZE, token = null) {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    size: String(size),
  });
  const response = await fetch(buildUrl(`/api/v1/search?${params.toString()}`), {
    headers: { ...authHeaders(token) },
  });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = await response.json();
  const results = data.items || [];
  const total = typeof data.total === 'number' ? data.total : results.length;
  return { results, total };
}

/**
 * Возвращает историю поисковых запросов пользователя.
 * @param {string} userId - идентификатор пользователя
 * @param {string} token - токен доступа
 * @param {{ limit?: number, offset?: number }} options - параметры пагинации
 * @returns {Promise<{ items: Array, total: number }>} элементы истории и их общее число
 */
export async function fetchSearchHistory(userId, token, { limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  const response = await fetch(
    buildUrl(`/api/v1/search/history/?${params.toString()}`),
    { headers: { ...authHeaders(token) } }
  );
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = await response.json();
  return { items: data.items || [], total: data.total || 0 };
}

/**
 * Очищает историю поисковых запросов пользователя.
 * @param {string} userId - идентификатор пользователя
 * @param {string} token - токен доступа
 * @returns {Promise<{ deleted: number, message: string }>} результат удаления
 */
export async function clearSearchHistory(userId, token) {
  const response = await fetch(buildUrl(`/api/v1/search/history/${userId}`), {
    method: 'DELETE',
    headers: { ...authHeaders(token) },
  });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  return response.json();
}
