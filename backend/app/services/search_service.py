import logging
from app.core.elastic import get_es_client
from app.core.config import settings

logger = logging.getLogger(__name__)

async def search_documents(query: str, limit: int = 10, offset: int = 0, document_id: str | None = None) -> list[dict]:
    es = get_es_client()
    index_name = settings.elasticsearch_index

    bool_query = {
        "must": [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["text", "file_name^2"],
                    "fuzziness": "AUTO"
                }
            }
        ]
    }

    if document_id:
        bool_query["filter"] = [{"term": {"document_id": document_id}}]

    body = {
            "query": {"bool": bool_query},
            "size": limit,
            "from": offset,
            "highlight": {
                "fields": {
                    "text": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]}
            }
        }
    }

    try:
        response = await es.search(index=index_name, body=body)
        hits = response.get("hits", {}).get("hits", [])
        
        results = []
        for hit in hits:
            source = hit["_source"]

            highlight = hit.get("highlight", {}).get("text", [])
            
            results.append({
                "chunk_id": source.get("chunk_id"),
                "document_id": source.get("document_id"),
                "file_name": source.get("file_name"),
                "page_number": source.get("page_number"),
                "text": source.get("text"),
                "score": hit.get("_score"),
                "highlights": highlight
            })
            
        return results
    except Exception as exc:
        logger.exception("Ошибка при поиске по запросу '%s': %s", query, exc)
        raise
