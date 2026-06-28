/**
 * Общие низкоуровневые помощники для работы с HTTP API бэкенда.
 */
import { API_BASE_URL } from '../config';

/** Собирает абсолютный URL из базового адреса и пути. */
export function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}

/** Формирует заголовок авторизации, если есть токен доступа. */
export function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Извлекает человекочитаемое сообщение об ошибке из ответа сервера.
 * @param {Response} response - объект ответа fetch
 * @returns {Promise<string>} текст ошибки
 */
export async function extractErrorMessage(response) {
  try {
    const data = await response.json();
    // FastAPI кладёт описание ошибки в поле detail.
    if (data && data.detail) {
      if (typeof data.detail === 'string') {
        return data.detail;
      }
      // Ошибки валидации (422) приходят массивом объектов.
      if (Array.isArray(data.detail)) {
        return data.detail
          .map((item) => item.msg || JSON.stringify(item))
          .join('; ');
      }
      return JSON.stringify(data.detail);
    }
    if (data && data.message) {
      return data.message;
    }
  } catch (e) {
    // тело не является JSON — игнорируем
  }
  return `Ошибка сервера (${response.status})`;
}
