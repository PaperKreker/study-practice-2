from pathlib import Path

import pytest

from app.services.parsing_service import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    _split_into_chunks,
    parse_docx,
    parse_document,
    parse_pdf,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_split_into_chunks_uses_expected_size_overlap_and_ids() -> None:
    text = "a" * (CHUNK_SIZE + 150)

    chunks = _split_into_chunks(
        text=text,
        page_number=3,
        chunk_id_offset=5,
        document_id="doc",
    )

    assert [chunk.chunk_id for chunk in chunks] == ["doc_5", "doc_6"]
    assert [chunk.page_number for chunk in chunks] == [3, 3]
    assert len(chunks[0].text) == CHUNK_SIZE
    assert len(chunks[1].text) == CHUNK_OVERLAP + 150


def test_parse_docx_extracts_text_from_valid_fixture() -> None:
    chunks = parse_docx((FIXTURES_DIR / "valid_small.docx").read_bytes(), "docx")

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "docx_0"
    assert chunks[0].page_number == 1
    assert "Elasticsearch" in chunks[0].text


def test_parse_pdf_extracts_text_from_valid_fixture() -> None:
    chunks = parse_pdf((FIXTURES_DIR / "valid_small.pdf").read_bytes(), "pdf")

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "pdf_0"
    assert chunks[0].page_number == 1
    assert "knowledge base search" in chunks[0].text


def test_empty_documents_return_no_chunks() -> None:
    assert parse_docx((FIXTURES_DIR / "empty.docx").read_bytes(), "empty-docx") == []
    assert parse_pdf((FIXTURES_DIR / "empty.pdf").read_bytes(), "empty-pdf") == []


@pytest.mark.parametrize(
    ("fixture_name", "extension"),
    [
        ("corrupted.pdf", ".pdf"),
        ("corrupted.docx", ".docx"),
        ("broken_formatting.docx", ".docx"),
    ],
)
def test_parse_document_raises_for_corrupted_fixtures(
    fixture_name: str, extension: str
) -> None:
    with pytest.raises(Exception):
        parse_document((FIXTURES_DIR / fixture_name).read_bytes(), extension, "broken")


def test_parse_document_rejects_unsupported_extension() -> None:
    with pytest.raises(ValueError):
        parse_document(b"plain text", ".txt", "doc")
