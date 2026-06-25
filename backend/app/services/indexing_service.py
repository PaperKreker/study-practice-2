import logging
from elasticsearch import helpers
from app.core.elastic import get_es_client
from app.core.config import settings
from app.services.parsing_service import TextChunk

logger = logging.getLogger(__name__)

async def index_document_chunks(
    document_id: str,
    file_name: str,
    chunks: list[TextChunk]
) -> int:
    es = get_es_client()
    index_name = settings.elasticsearch_index

    def generate_actions():
        for chunk in chunks:
            yield {
                "_index": index_name,
                "_id": chunk.chunk_id,
                "_source": {
                    "chunk_id": chunk.chunk_id,
                    "document_id": document_id,
                    "file_name": file_name,
                    "page_number": chunk.page_number,
                    "text": chunk.text,
                }
            }

    try:
        success, _ = await helpers.async_bulk(es, generate_actions())
        logger.info("Успешно проиндексировано %d чанков для документа '%s'", success, file_name)
        return success
    except Exception as exc:
        logger.exception("Ошибка при индексации документа '%s': %s", file_name, exc)
        raise
