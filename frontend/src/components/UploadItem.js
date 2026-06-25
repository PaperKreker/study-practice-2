import React from 'react';
import { UPLOAD_STATUS, STATUS_LABELS } from '../constants';
import { formatFileSize } from '../utils/format';

/**
 * Одна строка очереди загрузки: имя файла, прогресс-бар и текущее состояние
 * (Загрузка / Индексация / Готово / Ошибка).
 *
 * @param {{ item: Object, onRetry?: (item: Object) => void, onRemove?: (id: string) => void }} props
 *   item.localId   - локальный идентификатор записи в очереди
 *   item.name      - имя файла
 *   item.size      - размер файла в байтах
 *   item.progress  - прогресс загрузки 0..100
 *   item.status    - значение из UPLOAD_STATUS
 *   item.error     - текст ошибки (если status === ERROR)
 */
function UploadItem({ item, onRetry, onRemove }) {
  const { name, size, progress, status, error } = item;

  // На этапе индексации показываем «бегущий» неопределённый прогресс,
  // при загрузке — реальный процент.
  const isIndeterminate = status === UPLOAD_STATUS.INDEXING;
  const barWidth =
    status === UPLOAD_STATUS.DONE || status === UPLOAD_STATUS.ERROR
      ? 100
      : progress;

  return (
    <div className={`upload-item upload-item--${status}`}>
      <div className="upload-item__header">
        <span className="upload-item__name" title={name}>
          {name}
        </span>
        <span className="upload-item__size">{formatFileSize(size)}</span>
      </div>

      <div className="upload-item__bar">
        <div
          className={`upload-item__bar-fill${
            isIndeterminate ? ' upload-item__bar-fill--indeterminate' : ''
          }`}
          style={{ width: `${barWidth}%` }}
        />
      </div>

      <div className="upload-item__footer">
        <span className={`status-badge status-badge--${status}`}>
          {STATUS_LABELS[status]}
          {status === UPLOAD_STATUS.UPLOADING ? ` ${progress}%` : ''}
        </span>

        {status === UPLOAD_STATUS.ERROR && (
          <span className="upload-item__error" title={error}>
            {error}
          </span>
        )}

        <span className="upload-item__actions">
          {status === UPLOAD_STATUS.ERROR && onRetry && (
            <button
              type="button"
              className="link-button"
              onClick={() => onRetry(item)}
            >
              Повторить
            </button>
          )}
          {(status === UPLOAD_STATUS.DONE || status === UPLOAD_STATUS.ERROR) &&
            onRemove && (
              <button
                type="button"
                className="link-button"
                onClick={() => onRemove(item.localId)}
              >
                Убрать
              </button>
            )}
        </span>
      </div>
    </div>
  );
}

export default UploadItem;
