import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_user_create_strips_username() -> None:
    user = UserCreate(username="  student  ", password="secret1")

    assert user.username == "student"


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("   ", "secret1"),
        ("student", "short"),
        ("student", "x" * 73),
    ],
)
def test_user_create_rejects_invalid_credentials(username: str, password: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate(username=username, password=password)
