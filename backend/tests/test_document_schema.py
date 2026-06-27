from uuid import uuid4

from app.schemas.document import UploadResponse


def test_upload_response_accepts_valid_payload() -> None:
    document_id = uuid4()

    response = UploadResponse(
        document_id=document_id,
        file_name="lecture.pdf",
        size_bytes=128,
        message="Файл успешно загружен",
    )

    assert response.document_id == document_id
    assert response.file_name == "lecture.pdf"
    assert response.size_bytes == 128
    assert response.message == "Файл успешно загружен"


def test_upload_response_coerces_uuid_string() -> None:
    document_id = uuid4()

    response = UploadResponse(
        document_id=str(document_id),
        file_name="lecture.docx",
        size_bytes=256,
        message="ok",
    )

    assert response.document_id == document_id
