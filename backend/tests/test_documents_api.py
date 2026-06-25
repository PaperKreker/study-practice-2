import asyncio
from uuid import uuid4

import pytest

from app.api import documents


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

    monkeypatch.setattr(documents, "validate_file", fake_validate_file)

    assert asyncio.run(documents.upload(FakeUploadFile())) == expected_result
