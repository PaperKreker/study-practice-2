/**
 * Сервисный слой аутентификации.
 *
 * Контракт API:
 *   POST /api/v1/users/register — регистрация { username, password } -> TokenResponse
 *   POST /api/v1/users/login    — вход      { username, password } -> TokenResponse
 *   GET  /api/v1/users/me       — текущий пользователь (требует Bearer-токен)
 *
 * TokenResponse: { access_token, token_type, user: { id, username, is_active, created_at } }
 */
import { buildUrl, authHeaders, extractErrorMessage } from './http';

/** Общий помощник для POST-запросов с JSON-телом. */
async function postJson(path, body) {
  const response = await fetch(buildUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  return response.json();
}

/**
 * Регистрирует нового пользователя.
 * @param {string} username - имя пользователя
 * @param {string} password - пароль
 * @returns {Promise<Object>} TokenResponse
 */
export function registerRequest(username, password) {
  return postJson('/api/v1/users/register', { username, password });
}

/**
 * Выполняет вход пользователя.
 * @param {string} username - имя пользователя
 * @param {string} password - пароль
 * @returns {Promise<Object>} TokenResponse
 */
export function loginRequest(username, password) {
  return postJson('/api/v1/users/login', { username, password });
}

/**
 * Возвращает данные текущего пользователя по токену.
 * @param {string} token - токен доступа
 * @returns {Promise<Object>} UserResponse
 */
export async function fetchCurrentUser(token) {
  const response = await fetch(buildUrl('/api/v1/users/me'), {
    headers: { ...authHeaders(token) },
  });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  return response.json();
}
