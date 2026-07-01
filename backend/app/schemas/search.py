from pydantic import BaseModel


class SearchResultItem(BaseModel):
    """Отдельный результат полнотекстового поиска.

    Attributes:
        chunk_id (str): Идентификатор найденного текстового чанка.
        document_id (str): Идентификатор документа, которому принадлежит чанк.
        file_name (str): Имя файла документа.
        page (int | None): Номер страницы, на которой найден фрагмент.
        text (str): Текст найденного фрагмента.
        score (float): Оценка релевантности результата.
        highlights (list[str]): Подсвеченные фрагменты текста с совпадениями.
    """

    chunk_id: str
    document_id: str
    file_name: str
    page: int | None = None
    text: str
    score: float
    highlights: list[str] = []


class SearchResponse(BaseModel):
    """Ответ на поисковый запрос с общим количеством совпадений и результатами.

    Attributes:
        total (int): Общее количество найденных совпадений.
        items (list[SearchResultItem]): Список результатов на текущей странице.
    """

    total: int
    items: list[SearchResultItem]
