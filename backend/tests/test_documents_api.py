import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.api import documents
from app.services.parsing_service import TextChunk


class FakeUploadFile:
    filename = "lecture.pdf"


def test_upload_returns_validation_result(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_result = {
        "document_id": str(uuid4()),
        "file_name": "lecture.pdf",
        "size_bytes": 42,
        "message": "Файл успешно загружен",
    }

    async def fake_validate_file(file: FakeUploadFile) -> tuple[dict, bytes]:
        assert file.filename == "lecture.pdf"
        return expected_result, b"content"

    async def fake_process_document(
        document_id: str,
        file_name: str,
        file_bytes: bytes,
        extension: str,
    ) -> list[TextChunk]:
        assert document_id == expected_result["document_id"]
        assert file_name == "lecture.pdf"
        assert file_bytes == b"content"
        assert extension == ".pdf"
        return [TextChunk(chunk_id=f"{document_id}_0", page_number=1, text="content")]

    async def fake_index_document_chunks(
        document_id: str,
        file_name: str,
        chunks: list[TextChunk],
    ) -> int:
        assert document_id == expected_result["document_id"]
        assert file_name == "lecture.pdf"
        assert len(chunks) == 1
        return 1

    async def fake_create_document_metadata(db, metadata: dict, chunk_count: int):
        assert db is fake_db
        assert metadata == expected_result
        assert chunk_count == 1

    monkeypatch.setattr(documents, "validate_file", fake_validate_file)
    monkeypatch.setattr(documents, "process_document", fake_process_document)
    monkeypatch.setattr(documents, "index_document_chunks", fake_index_document_chunks)
    monkeypatch.setattr(documents, "create_document_metadata", fake_create_document_metadata)

    fake_db = object()
    result = asyncio.run(documents.upload(FakeUploadFile(), db=fake_db))

    assert result["document_id"] == expected_result["document_id"]
    assert result["file_name"] == "lecture.pdf"
    assert result["size_bytes"] == 42
    assert "1" in result["message"]


def test_upload_does_not_save_metadata_when_indexing_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metadata = {
        "document_id": str(uuid4()),
        "file_name": "lecture.pdf",
        "size_bytes": 7,
        "message": "validated",
    }

    async def fake_validate_file(file):
        return metadata, b"content"

    async def fake_process_document(**kwargs):
        return [TextChunk(chunk_id="chunk-1", page_number=1, text="content")]

    async def fake_index_document_chunks(**kwargs):
        raise RuntimeError("Elasticsearch unavailable")

    async def unexpected_create(*args, **kwargs):
        pytest.fail("metadata must not be stored after an indexing failure")

    monkeypatch.setattr(documents, "validate_file", fake_validate_file)
    monkeypatch.setattr(documents, "process_document", fake_process_document)
    monkeypatch.setattr(documents, "index_document_chunks", fake_index_document_chunks)
    monkeypatch.setattr(documents, "create_document_metadata", unexpected_create)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(documents.upload(FakeUploadFile(), db=object()))

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_list_documents_forwards_pagination(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_db = object()
    expected_items = [SimpleNamespace(file_name="lecture.pdf")]

    async def fake_get_all_documents(db, limit: int, offset: int):
        assert db is fake_db
        assert (limit, offset) == (20, 40)
        return expected_items, 81

    monkeypatch.setattr(documents, "get_all_documents", fake_get_all_documents)

    result = asyncio.run(documents.list_documents(limit=20, offset=40, db=fake_db))

    assert result == {"total": 81, "items": expected_items}


def test_get_document_returns_found_document(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_db = object()
    expected = SimpleNamespace(id=uuid4(), file_name="lecture.pdf")

    async def fake_get_document_by_id(db, document_id: str):
        assert db is fake_db
        assert document_id == "document-id"
        return expected

    monkeypatch.setattr(documents, "get_document_by_id", fake_get_document_by_id)

    assert asyncio.run(documents.get_document("document-id", db=fake_db)) is expected


def test_get_document_returns_404_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get_document_by_id(db, document_id: str):
        return None

    monkeypatch.setattr(documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(documents.get_document("missing", db=object()))

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_document_removes_chunks_and_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_db = object()
    document = SimpleNamespace(file_name="lecture.pdf")

    async def fake_get_document_by_id(db, document_id: str):
        return document

    async def fake_delete_document_chunks(document_id: str):
        assert document_id == "document-id"
        return 3

    async def fake_delete_document_from_db(db, document_id: str):
        assert db is fake_db
        assert document_id == "document-id"
        return True

    monkeypatch.setattr(documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(documents, "delete_document_chunks", fake_delete_document_chunks)
    monkeypatch.setattr(documents, "delete_document_from_db", fake_delete_document_from_db)

    result = asyncio.run(documents.delete_document("document-id", db=fake_db))

    assert result["document_id"] == "document-id"
    assert result["chunks_deleted"] == 3


def test_delete_document_returns_404_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_document_by_id(db, document_id: str):
        return None

    monkeypatch.setattr(documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(documents.delete_document("missing", db=object()))

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
