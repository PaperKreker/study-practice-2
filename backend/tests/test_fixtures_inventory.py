from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile, is_zipfile

FIXTURES_DIR = Path(__file__).parent / "fixtures"

REQUIRED_FIXTURES = {
    "valid_small.pdf",
    "valid_small.docx",
    "empty.pdf",
    "empty.docx",
    "corrupted.pdf",
    "corrupted.docx",
    "broken_formatting.docx",
    "non_standard_font.pdf",
}


def test_qa03_fixture_set_is_present() -> None:
    existing_files = {path.name for path in FIXTURES_DIR.iterdir() if path.is_file()}

    assert REQUIRED_FIXTURES <= existing_files


def test_pdf_fixtures_have_expected_signatures() -> None:
    valid_pdf_names = {"valid_small.pdf", "empty.pdf", "non_standard_font.pdf"}

    for fixture_name in valid_pdf_names:
        content = (FIXTURES_DIR / fixture_name).read_bytes()
        assert content.startswith(b"%PDF-")
        assert content.rstrip().endswith(b"%%EOF")


def test_valid_docx_fixtures_are_zip_packages() -> None:
    valid_docx_names = {"valid_small.docx", "empty.docx"}

    for fixture_name in valid_docx_names:
        assert is_zipfile(FIXTURES_DIR / fixture_name)


def test_corrupted_docx_is_not_zip_package() -> None:
    assert not is_zipfile(FIXTURES_DIR / "corrupted.docx")


def test_broken_formatting_docx_contains_malformed_document_xml() -> None:
    fixture_path = FIXTURES_DIR / "broken_formatting.docx"

    assert is_zipfile(fixture_path)
    with ZipFile(fixture_path) as archive:
        document_xml = archive.read("word/document.xml")

    try:
        ElementTree.fromstring(document_xml)
    except ElementTree.ParseError:
        return

    raise AssertionError("broken_formatting.docx should contain malformed XML")


def test_corrupted_pdf_is_incomplete() -> None:
    content = (FIXTURES_DIR / "corrupted.pdf").read_bytes()

    assert content.startswith(b"%PDF-")
    assert not content.rstrip().endswith(b"%%EOF")
