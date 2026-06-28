import React from 'react';
import {formatDate, formatFileSize} from '../utils/format';

/**
 * Список уже загруженных документов с названием, датой загрузки и размером.
 * Для собственных документов пользователя показывает кнопку удаления.
 * Адаптивен: на широких экранах — таблица, на узких — карточки
 * (управляется через CSS).
 *
 * @param {{
 *   documents: Array,
 *   loading: boolean,
 *   error: string|null,
 *   onRefresh: () => void,
 *   currentUserId?: string,
 *   onDelete?: (doc: Object) => void,
 *   deletingId?: string|null,
 * }} props
 */
function DocumentList({
  documents,
  loading,
  error,
  onRefresh,
  currentUserId,
  onDelete,
  deletingId,
}) {
  return (
    <section className="doc-list">
      <div className="doc-list__header">
        <h2 className="section-title">Загруженные документы</h2>
        <button
          type="button"
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? 'Обновление...' : 'Обновить'}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {!error && documents.length === 0 && !loading && (
        <p className="muted-text">Пока нет загруженных документов.</p>
      )}

      {documents.length > 0 && (
        <div className="doc-list__table" role="table">
          <div className="doc-list__row doc-list__row--head" role="row">
            <span role="columnheader">Название</span>
            <span role="columnheader">Дата загрузки</span>
            <span role="columnheader">Размер</span>
            <span role="columnheader" aria-label="Действия"></span>
          </div>
          {documents.map((doc) => {
            const id = doc.id || doc.document_id || doc.file_name;
            // Удалять можно только собственные документы.
            const isOwn =
              Boolean(onDelete) &&
              Boolean(currentUserId) &&
              doc.user_id === currentUserId;
            return (
              <div className="doc-list__row" role="row" key={id}>
                <span className="doc-list__name" role="cell" title={doc.file_name}>
                  <span className="doc-list__file-icon" aria-hidden="true">
                    📄
                  </span>
                  {doc.file_name}
                </span>
                <span className="doc-list__date" role="cell">
                  {formatDate(doc.uploaded_at || doc.created_at)}
                </span>
                <span className="doc-list__size" role="cell">
                    {formatFileSize(doc.size_bytes)}
                </span>
                <span className="doc-list__actions" role="cell">
                  {isOwn && (
                    <button
                      type="button"
                      className="danger-button"
                      onClick={() => onDelete(doc)}
                      disabled={deletingId === id}
                      aria-label={`Удалить ${doc.file_name}`}
                    >
                      {deletingId === id ? 'Удаление...' : 'Удалить'}
                    </button>
                  )}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default DocumentList;
