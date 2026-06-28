import logging
from app.core.elastic import get_es_client
from app.core.config import settings

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.search_history import SearchHistory
from app.models.document import Document

logger = logging.getLogger(__name__)


async def search_documents(
    db: AsyncSession,
    query: str,
    user_id: uuid.UUID,
    page: int = 1,
    size: int = 10,
    document_id: str | None = None,
    filter_by_user: bool = False,
) -> dict:
    es = get_es_client()
    index_name = settings.elasticsearch_index

    from_offset = (page - 1) * size

    bool_query = {
        "must": [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["text", "file_name^2"],
                    "fuzziness": "AUTO",
                }
            }
        ]
    }

    if "filter" not in bool_query:
        bool_query["filter"] = []

    if document_id:
        bool_query["filter"].append({"term": {"document_id": document_id}})

    if filter_by_user:
        stmt = select(Document.id).where(Document.user_id == user_id)
        res = await db.execute(stmt)
        user_doc_ids = [str(uid) for uid in res.scalars().all()]

        if not user_doc_ids:
            return {"total": 0, "items": []}

        bool_query["filter"].append({"terms": {"document_id": user_doc_ids}})

    if not bool_query["filter"]:
        del bool_query["filter"]

    body = {
        "query": {"bool": bool_query},
        "size": size,
        "from": from_offset,
        "highlight": {
            "fields": {"text": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]}}
        },
    }

    try:
        response = await es.search(index=index_name, body=body)
        hits = response.get("hits", {}).get("hits", [])

        total_hits = response.get("hits", {}).get("total", {}).get("value", 0)

        results = []
        for hit in hits:
            source = hit["_source"]
            highlight = hit.get("highlight", {}).get("text", [])

            results.append(
                {
                    "chunk_id": source.get("chunk_id"),
                    "document_id": source.get("document_id"),
                    "file_name": source.get("file_name"),
                    "page": source.get("page_number"),
                    "text": source.get("text"),
                    "score": hit.get("_score"),
                    "highlights": highlight,
                }
            )

        history_entry = SearchHistory(
            query=query,
            results_count=total_hits,
            user_id=user_id,
            document_id=uuid.UUID(document_id) if document_id else None,
        )
        db.add(history_entry)
        await db.commit()

        return {"total": total_hits, "items": results}
    except Exception as exc:
        logger.exception("Ошибка при поиске по запросу '%s': %s", query, exc)
        raise
