from datetime import datetime, timedelta, timezone

import jwt

from app.core import security


def test_hash_and_verify_password() -> None:
    hashed = security.hash_password("correct-password")

    assert hashed != "correct-password"
    assert security.verify_password("correct-password", hashed) is True
    assert security.verify_password("wrong-password", hashed) is False


def test_access_token_round_trip() -> None:
    token = security.create_access_token("user-id")

    assert security.decode_access_token(token) == "user-id"


def test_decode_access_token_rejects_invalid_token() -> None:
    assert security.decode_access_token("not-a-jwt") is None


def test_decode_access_token_rejects_expired_token() -> None:
    token = jwt.encode(
        {
            "sub": "user-id",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        security.settings.secret_key,
        algorithm=security.settings.algorithm,
    )

    assert security.decode_access_token(token) is None
