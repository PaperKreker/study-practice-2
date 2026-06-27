import asyncio
from uuid import UUID

import pytest
from fastapi import HTTPException, status

from app.services.document_service import MAX_FILE_SIZE, validate_file


class FakeUploadFile:
    def __init__(self, filename: str, contents: bytes) -> None:
        self.filename = filename
        self._contents = contents

    async def read(self) -> bytes:
        return self._contents


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
