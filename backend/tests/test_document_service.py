import asyncio
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException, status

from app.services.document_service import (
    MAX_FILE_SIZE,
    create_document_metadata,
    delete_document_from_db,
    get_all_documents,
    get_document_by_id,
    validate_file,
)


class FakeUploadFile:
    def __init__(self, filename: str, contents: bytes) -> None:
        self.filename = filename
        self._contents = contents

    async def read(self) -> bytes:
        return self._contents


class FakeResult:
    def __init__(self, scalar=None, items=None) -> None:
        self.scalar = scalar
        self.items = items or []

    def scalar_one(self):
        return self.scalar

    def scalar_one_or_none(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.items


class FakeDatabase:
    def __init__(self, results=None) -> None:
        self.results = list(results or [])
        self.statements = []
        self.added = []
        self.deleted = []
        self.commit_count = 0

    async def execute(self, statement):
        self.statements.append(statement)
        return self.results.pop(0)

    def add(self, value) -> None:
        self.added.append(value)

    async def delete(self, value) -> None:
        self.deleted.append(value)

    async def commit(self) -> None:
        self.commit_count += 1


@pytest.mark.parametrize(
    ("filename", "contents"),
    [
        ("lecture.pdf", b"%PDF-1.7\ncontent"),
        ("practice.docx", b"PK\x03\x04content"),
        ("UPPER.PDF", b"%PDF-1.7\ncontent"),
        ("UPPER.DOCX", b"PK\x03\x04content"),
        ("лекция.pdf", b"%PDF-1.7\ncontent"),
    ],
)
def test_validate_file_accepts_allowed_extensions(
    filename: str, contents: bytes
) -> None:
    result, file_bytes = asyncio.run(validate_file(FakeUploadFile(filename, contents)))

    UUID(result["document_id"])
    assert result["file_name"] == filename
    assert result["size_bytes"] == len(contents)
    assert result["message"] == "Файл успешно загружен"
    assert file_bytes == contents


@pytest.mark.parametrize(
    "filename", ["notes.txt", "image.png", "archive.zip", "no_extension"]
)
def test_validate_file_rejects_disallowed_extensions(filename: str) -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(validate_file(FakeUploadFile(filename, b"content")))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Допустимы только PDF и DOCX"


def test_validate_file_accepts_file_at_size_limit() -> None:
    contents = b"x" * MAX_FILE_SIZE

    result, file_bytes = asyncio.run(
        validate_file(FakeUploadFile("limit.pdf", contents))
    )

    assert result["size_bytes"] == MAX_FILE_SIZE
    assert file_bytes == contents


def test_validate_file_rejects_file_over_size_limit() -> None:
    contents = b"x" * (MAX_FILE_SIZE + 1)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(validate_file(FakeUploadFile("too-large.pdf", contents)))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Размер файла превышает 20 МБ"


def test_validate_file_generates_unique_document_ids() -> None:
    first, _ = asyncio.run(validate_file(FakeUploadFile("first.pdf", b"first")))
    second, _ = asyncio.run(validate_file(FakeUploadFile("second.pdf", b"second")))

    assert first["document_id"] != second["document_id"]


def test_create_document_metadata_persists_document() -> None:
    db = FakeDatabase()
    document_id = uuid4()
    metadata = {
        "document_id": str(document_id),
        "file_name": "lecture.pdf",
        "size_bytes": 128,
    }

    document = asyncio.run(create_document_metadata(db, metadata, chunk_count=4))

    assert document.id == document_id
    assert document.file_name == "lecture.pdf"
    assert document.size_bytes == 128
    assert document.chunk_count == 4
    assert document.user_id is None
    assert db.added == [document]
    assert db.commit_count == 1


def test_get_all_documents_returns_items_and_total() -> None:
    expected_items = [object(), object()]
    db = FakeDatabase(results=[FakeResult(scalar=7), FakeResult(items=expected_items)])

    items, total = asyncio.run(get_all_documents(db, limit=2, offset=4))

    assert items == expected_items
    assert total == 7
    assert len(db.statements) == 2


def test_get_document_by_id_returns_none_for_invalid_uuid() -> None:
    db = FakeDatabase()

    assert asyncio.run(get_document_by_id(db, "not-a-uuid")) is None
    assert db.statements == []


def test_get_document_by_id_returns_database_result() -> None:
    expected = object()
    db = FakeDatabase(results=[FakeResult(scalar=expected)])

    assert asyncio.run(get_document_by_id(db, str(uuid4()))) is expected
    assert len(db.statements) == 1


def test_delete_document_from_db_deletes_existing_document() -> None:
    expected = object()
    db = FakeDatabase(results=[FakeResult(scalar=expected)])

    assert asyncio.run(delete_document_from_db(db, str(uuid4()))) is True
    assert db.deleted == [expected]
    assert db.commit_count == 1


def test_delete_document_from_db_returns_false_when_missing() -> None:
    db = FakeDatabase(results=[FakeResult(scalar=None)])

    assert asyncio.run(delete_document_from_db(db, str(uuid4()))) is False
    assert db.deleted == []
    assert db.commit_count == 0
