import re
from pathlib import Path


INIT_SCRIPT = Path(__file__).parents[2] / "init.sh"


def test_init_script_contains_ten_unique_pdf_sources() -> None:
    content = INIT_SCRIPT.read_text(encoding="utf-8")
    urls = re.findall(r'"(https?://[^\"]+\.pdf)"', content)

    assert len(urls) == 10
    assert len(set(urls)) == 10


def test_init_script_uses_current_authenticated_api_contract() -> None:
    content = INIT_SCRIPT.read_text(encoding="utf-8")

    assert 'LOGIN_URL="$BACKEND_API_URL/users/login"' in content
    assert 'REGISTER_URL="$BACKEND_API_URL/users/register"' in content
    assert 'UPLOAD_URL="$BACKEND_API_URL/documents/upload"' in content
    assert 'Authorization: Bearer $TOKEN' in content
    assert 'if [ "$http_code" -eq 201 ]' in content
