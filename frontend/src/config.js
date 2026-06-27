/**
 * Глобальная конфигурация фронтенд-приложения.
 *
 * API_BASE_URL берётся из переменной окружения REACT_APP_API_URL.
 * Если переменная не задана, используется пустая строка — запросы уходят
 * по относительному пути. Это работает как в dev-режиме (через "proxy" в
 * package.json), так и в production (когда статику отдаёт Nginx, который
 * проксирует /api на бэкенд).
 */
export const API_BASE_URL = process.env.REACT_APP_API_URL || '';

/** Допустимые MIME-типы загружаемых документов. */
export const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

/** Допустимые расширения файлов (запасная проверка, если MIME пустой). */
export const ALLOWED_EXTENSIONS = ['.pdf', '.docx'];

/** Максимальный размер файла — 20 МБ. */
export const MAX_FILE_SIZE = 20 * 1024 * 1024;

/** Количество результатов поиска на одну страницу. */
export const PAGE_SIZE = 10;
