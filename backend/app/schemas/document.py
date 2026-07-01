from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Ответ на успешную загрузку документа.

    Attributes:
        document_id (UUID): Идентификатор созданного документа.
        file_name (str): Имя загруженного файла.
        size_bytes (int): Размер файла в байтах.
        message (str): Сообщение о результате операции.
    """

    document_id: UUID
    file_name: str
    size_bytes: int
    message: str


class DocumentResponse(BaseModel):
    """Подробная информация о документе.

    Attributes:
        id (UUID): Идентификатор документа.
        file_name (str): Имя файла.
        size_bytes (int): Размер файла в байтах.
        chunk_count (int): Количество текстовых чанков документа.
        uploaded_at (datetime): Дата и время загрузки.
        user_id (UUID | None): Идентификатор пользователя-владельца, если есть.
    """

    id: UUID
    file_name: str
    size_bytes: int
    chunk_count: int
    uploaded_at: datetime
    user_id: UUID | None = None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Список документов с общим количеством для пагинации.

    Attributes:
        total (int): Общее количество документов, удовлетворяющих запросу.
        items (list[DocumentResponse]): Список документов на текущей странице.
    """

    total: int
    items: list[DocumentResponse]
