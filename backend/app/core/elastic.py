import logging
from elasticsearch import AsyncElasticsearch, NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)

es_client: AsyncElasticsearch | None = None

INDEX_MAPPINGS = {
    "properties": {
        "chunk_id": {"type": "keyword"},
        "document_id": {"type": "keyword"},
        "file_name": {"type": "keyword"},
        "page_number": {"type": "integer"},
        "text": {
            "type": "text",
            "analyzer": "russian",
        },
    }
}


def get_es_client() -> AsyncElasticsearch:
    if es_client is None:
        raise RuntimeError("Elasticsearch client не инициализирован")
    return es_client


async def init_elasticsearch() -> None:
    global es_client

    logger.debug("Подключение к Elasticsearch по адресу: %s", settings.elasticsearch_url)

    es_client = AsyncElasticsearch(settings.elasticsearch_url)
    index_name = settings.elasticsearch_index

    try:
        await es_client.indices.get(index=index_name)
        logger.info("Индекс '%s' уже существует.", index_name)
    except NotFoundError:
        logger.info("Индекс '%s' не найден. Создаю...", index_name)
        await es_client.indices.create(index=index_name, mappings=INDEX_MAPPINGS)


async def close_elasticsearch() -> None:
    global es_client
    if es_client is not None:
        await es_client.close()
        es_client = None
        logger.debug("Elasticsearch клиент закрыт.")
