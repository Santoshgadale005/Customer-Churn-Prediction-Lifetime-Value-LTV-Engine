from datetime import timedelta

from jose import jwt

from app.services.auth_service import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    password = "password123"
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-password", hashed_password)


def test_create_access_token_contains_subject():
    token = create_access_token(
        {"sub": "santosh", "role": "admin", "user_id": 1},
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "santosh"
    assert payload["role"] == "admin"
    assert payload["user_id"] == 1
