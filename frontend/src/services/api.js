/**
 * Сервисный слой для взаимодействия с REST API бэкенда.
 *
 * Документы и история требуют авторизации (Bearer-токен). Поиск работает
 * и без авторизации — для авторизованных пользователей токен передаётся,
 * чтобы бэкенд сохранял запрос в серверной истории.
 *
 * Контракт API:
 *   POST   /api/v1/documents/upload          — загрузка файла (multipart, поле "file")
 *   GET    /api/v1/documents                 — список загруженных документов
 *   GET    /api/v1/documents/{id}            — статус конкретного документа
 *   DELETE /api/v1/documents/{id}            — удаление своего документа
 *   GET    /api/v1/search?q=&page=&size=     — полнотекстовый поиск
 *   GET    /api/v1/search/history            — история поисковых запросов пользователя
 *   DELETE /api/v1/search/history            — очистка истории пользователя
 */
import { PAGE_SIZE } from '../config';
import { buildUrl, authHeaders, extractErrorMessage } from './http';

/**
 * Выполняет fetch, добавляя заголовок авторизации только при наличии токена.
 * Без токена запрос уходит одним аргументом — это сохраняет совместимость
 * с эндпоинтами, не требующими авторизации.
 */
function authedFetch(url, token, init = {}) {
  const headers = { ...authHeaders(token), ...(init.headers || {}) };
  const hasHeaders = Object.keys(headers).length > 0;
  const hasOtherInit = Object.keys(init).some((key) => key !== 'headers');
  // Без токена и без дополнительных опций отправляем запрос одним аргументом.
  if (!hasHeaders && !hasOtherInit) {
    return fetch(url);
  }
  return fetch(url, { ...init, headers });
}

/**
 * Загружает один файл на сервер с отслеживанием прогресса загрузки.
 * Используется XMLHttpRequest, так как fetch не умеет отдавать прогресс upload.
 *
 * @param {File} file - загружаемый файл
 * @param {(percent: number) => void} onProgress - колбэк прогресса (0..100)
 * @param {string} token - токен доступа
 * @returns {Promise<Object>} данные созданного документа { id, file_name, status, ... }
 */
export function uploadDocument(file, onProgress, token) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.open('POST', buildUrl('/api/v1/documents/upload'));
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    }

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
 * Возвращает список загруженных документов.
 * @param {string} token - токен доступа
 * @param {{ limit?: number, offset?: number, myDocs?: boolean }} options - параметры запроса
 * @returns {Promise<Array>} массив документов
 */
export async function fetchDocuments(token, { limit, offset, myDocs } = {}) {
  const params = new URLSearchParams();
  if (typeof limit === 'number') params.set('limit', String(limit));
  if (typeof offset === 'number') params.set('offset', String(offset));
  if (myDocs) params.set('my_docs', 'true');
  const query = params.toString();

  const response = await authedFetch(
    buildUrl(`/api/v1/documents${query ? `?${query}` : ''}`),
    token
  );
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
 * @param {string} token - токен доступа
 * @returns {Promise<Object>} документ со статусом
 */
export async function fetchDocumentStatus(id, token) {
  const response = await authedFetch(buildUrl(`/api/v1/documents/${id}`), token);
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  return response.json();
}

/**
 * Удаляет документ пользователя по идентификатору.
 * @param {string} id - идентификатор документа
 * @param {string} token - токен доступа
 * @returns {Promise<void>}
 */
export async function deleteDocument(id, token) {
  const response = await authedFetch(buildUrl(`/api/v1/documents/${id}`), token, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
}

/**
 * Выполняет полнотекстовый поиск по документам.
 *
 * @param {string} query - поисковый запрос
 * @param {number} page - номер страницы (с 1)
 * @param {number} size - размер страницы
 * @param {string} token - токен доступа (необязательно)
 * @returns {Promise<{ results: Array, total: number }>} результаты и общее число совпадений
 */
export async function searchDocuments(query, page = 1, size = PAGE_SIZE, token = null) {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    size: String(size),
  });
  const response = await authedFetch(
    buildUrl(`/api/v1/search?${params.toString()}`),
    token
  );
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = await response.json();

  // Бэкенд может вернуть { items, total } или просто массив.
  if (Array.isArray(data)) {
    return { results: data, total: data.length };
  }
  const results = data.items || data.results || [];
  const total = typeof data.total === 'number' ? data.total : results.length;
  return { results, total };
}

/**
 * Возвращает историю поисковых запросов текущего пользователя.
 * Пользователь определяется бэкендом по токену.
 * @param {string} token - токен доступа
 * @param {{ limit?: number, offset?: number }} options - параметры пагинации
 * @returns {Promise<{ items: Array, total: number }>} элементы истории и их общее число
 */
export async function fetchSearchHistory(token, { limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  const response = await authedFetch(
    buildUrl(`/api/v1/search/history?${params.toString()}`),
    token
  );
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = await response.json();
  return { items: data.items || [], total: data.total || 0 };
}

/**
 * Очищает историю поисковых запросов текущего пользователя.
 * @param {string} token - токен доступа
 * @returns {Promise<{ deleted: number, message: string }>} результат удаления
 */
export async function clearSearchHistory(token) {
  const response = await authedFetch(buildUrl('/api/v1/search/history'), token, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  return response.json();
}
