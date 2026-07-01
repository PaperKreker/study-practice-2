from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HistoryItem(BaseModel):
    """Отдельная запись истории поисковых запросов.

    Attributes:
        id (UUID): Идентификатор записи истории.
        query (str): Текст поискового запроса.
        results_count (int): Количество найденных результатов.
        created_at (datetime): Дата и время выполнения запроса.
        document_id (UUID | None): Идентификатор документа, если поиск был ограничен им.
    """

    id: UUID
    query: str
    results_count: int
    created_at: datetime
    document_id: UUID | None = None

    model_config = {"from_attributes": True}


class HistoryListResponse(BaseModel):
    """Список записей истории поиска с общим количеством для пагинации.

    Attributes:
        total (int): Общее количество записей истории.
        items (list[HistoryItem]): Список записей на текущей странице.
    """

    total: int
    items: list[HistoryItem]


class DeleteHistoryResponse(BaseModel):
    """Результат удаления истории поисковых запросов.

    Attributes:
        deleted (int): Количество удаленных записей.
        message (str): Сообщение о результате операции.
    """

    deleted: int
    message: str
