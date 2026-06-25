import React, { useRef, useState } from 'react';
import { ALLOWED_EXTENSIONS } from '../config';

/**
 * Зона загрузки документов с поддержкой Drag-and-Drop и множественного
 * выбора файлов.
 *
 * @param {{ onFilesSelected: (files: File[]) => void, disabled?: boolean }} props
 *   onFilesSelected - вызывается со списком выбранных файлов
 *   disabled        - блокирует взаимодействие
 */
function DropZone({ onFilesSelected, disabled }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  /** Передаёт выбранные файлы наверх. */
  const handleFiles = (fileList) => {
    const files = Array.from(fileList || []);
    if (files.length > 0) {
      onFilesSelected(files);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);
    if (disabled) return;
    handleFiles(event.dataTransfer.files);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    if (!disabled) setIsDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleClick = () => {
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  };

  const handleInputChange = (event) => {
    handleFiles(event.target.files);
    // Сбрасываем значение, чтобы можно было выбрать тот же файл повторно.
    event.target.value = '';
  };

  return (
    <div
      className={`dropzone${isDragOver ? ' dropzone--active' : ''}${
        disabled ? ' dropzone--disabled' : ''
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label="Область загрузки документов"
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ALLOWED_EXTENSIONS.join(',')}
        className="dropzone__input"
        onChange={handleInputChange}
        disabled={disabled}
      />
      <div className="dropzone__icon" aria-hidden="true">
        ⬆
      </div>
      <p className="dropzone__title">
        Перетащите файлы сюда или нажмите для выбора
      </p>
      <p className="dropzone__hint">
        Поддерживаются PDF и DOCX, до 20 МБ. Можно загружать несколько файлов.
      </p>
    </div>
  );
}

export default DropZone;
