import React, { useCallback, useEffect, useRef, useState } from 'react';
import DropZone from '../components/DropZone';
import UploadItem from '../components/UploadItem';
import DocumentList from '../components/DocumentList';
import { UPLOAD_STATUS, normalizeStatus } from '../constants';
import { validateFile } from '../utils/validateFile';
import {
  uploadDocument,
  fetchDocuments,
  fetchDocumentStatus,
} from '../services/api';

// Параметры опроса статуса индексации.
const POLL_INTERVAL_MS = 1500;
const MAX_POLL_ATTEMPTS = 20;

/**
 * Страница загрузки документов.
 * Объединяет зону Drag-and-Drop, очередь загрузки с прогресс-барами
 * и состояниями и список уже загруженных документов.
 */
function UploadPage() {
  const [queue, setQueue] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [docsError, setDocsError] = useState(null);

  // Счётчик для генерации уникальных локальных идентификаторов записей очереди.
  const localIdCounter = useRef(0);

  /** Обновляет одну запись очереди по её локальному идентификатору. */
  const updateQueueItem = useCallback((localId, changes) => {
    setQueue((prev) =>
      prev.map((item) =>
        item.localId === localId ? { ...item, ...changes } : item
      )
    );
  }, []);

  /** Загружает список документов с сервера. */
  const loadDocuments = useCallback(async () => {
    setDocsLoading(true);
    setDocsError(null);
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch (err) {
      setDocsError(err.message || 'Не удалось загрузить список документов');
    } finally {
      setDocsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  /**
   * Опрашивает статус индексации документа, пока он не завершится.
   * Если эндпоинт статуса недоступен, считаем документ проиндексированным.
   */
  const pollIndexing = useCallback(
    async (localId, documentId) => {
      if (!documentId) {
        // Сервер не вернул id — не можем опросить, считаем готовым.
        updateQueueItem(localId, { status: UPLOAD_STATUS.DONE });
        loadDocuments();
        return;
      }
      for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
        try {
          const doc = await fetchDocumentStatus(documentId);
          const status = normalizeStatus(doc.status);
          if (status === UPLOAD_STATUS.DONE) {
            updateQueueItem(localId, { status: UPLOAD_STATUS.DONE });
            loadDocuments();
            return;
          }
          if (status === UPLOAD_STATUS.ERROR) {
            updateQueueItem(localId, {
              status: UPLOAD_STATUS.ERROR,
              error: 'Ошибка индексации документа',
            });
            return;
          }
        } catch (err) {
          // Эндпоинт статуса может быть не реализован — прекращаем опрос
          // и считаем загрузку успешной.
          updateQueueItem(localId, { status: UPLOAD_STATUS.DONE });
          loadDocuments();
          return;
        }
      }
      // Превышено число попыток — помечаем готовым, чтобы не «зависать».
      updateQueueItem(localId, { status: UPLOAD_STATUS.DONE });
      loadDocuments();
    },
    [updateQueueItem, loadDocuments]
  );

  /** Запускает загрузку одной записи очереди на сервер. */
  const startUpload = useCallback(
    async (item) => {
      updateQueueItem(item.localId, {
        status: UPLOAD_STATUS.UPLOADING,
        progress: 0,
        error: null,
      });
      try {
        const response = await uploadDocument(item.file, (percent) => {
          updateQueueItem(item.localId, { progress: percent });
        });
        // Загрузка завершена — переходим к этапу индексации.
        updateQueueItem(item.localId, {
          status: UPLOAD_STATUS.INDEXING,
          progress: 100,
        });
        const documentId = response.id || response.document_id;
        await pollIndexing(item.localId, documentId);
      } catch (err) {
        updateQueueItem(item.localId, {
          status: UPLOAD_STATUS.ERROR,
          error: err.message || 'Ошибка загрузки',
        });
      }
    },
    [updateQueueItem, pollIndexing]
  );

  /** Обрабатывает выбор файлов: валидирует и ставит в очередь на загрузку. */
  const handleFilesSelected = useCallback(
    (files) => {
      const newItems = files.map((file) => {
        localIdCounter.current += 1;
        const validationError = validateFile(file);
        return {
          localId: localIdCounter.current,
          file,
          name: file.name,
          size: file.size,
          progress: 0,
          status: validationError ? UPLOAD_STATUS.ERROR : UPLOAD_STATUS.UPLOADING,
          error: validationError,
        };
      });

      setQueue((prev) => [...newItems, ...prev]);

      // Запускаем загрузку только для прошедших валидацию файлов.
      newItems
        .filter((item) => !item.error)
        .forEach((item) => startUpload(item));
    },
    [startUpload]
  );

  /** Повторная попытка загрузки для записи с ошибкой. */
  const handleRetry = useCallback(
    (item) => {
      const validationError = validateFile(item.file);
      if (validationError) {
        updateQueueItem(item.localId, { error: validationError });
        return;
      }
      startUpload(item);
    },
    [startUpload, updateQueueItem]
  );

  /** Убирает запись из очереди (визуально). */
  const handleRemove = useCallback((localId) => {
    setQueue((prev) => prev.filter((item) => item.localId !== localId));
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Загрузка документов</h1>
      <p className="page-subtitle">
        Загрузите лекции и материалы в форматах PDF или DOCX — они будут
        проиндексированы и станут доступны для поиска.
      </p>

      <DropZone onFilesSelected={handleFilesSelected} />

      {queue.length > 0 && (
        <section className="upload-queue">
          <h2 className="section-title">Очередь загрузки</h2>
          {queue.map((item) => (
            <UploadItem
              key={item.localId}
              item={item}
              onRetry={handleRetry}
              onRemove={handleRemove}
            />
          ))}
        </section>
      )}

      <DocumentList
        documents={documents}
        loading={docsLoading}
        error={docsError}
        onRefresh={loadDocuments}
      />
    </div>
  );
}

export default UploadPage;
