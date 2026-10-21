from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from backend.app.core.security import CSRF_COOKIE, SESSION_COOKIE, password_hasher
from backend.app.main import create_app
from backend.app.models import User
from fastapi.testclient import TestClient
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.orm import Session

ACCOUNT = {"email": "Persona@Example.com", "password": "una-clave-larga-2026"}


def register_and_login(client):
    response = client.post("/api/auth/register", json=ACCOUNT)
    assert response.status_code == 201
    response = client.post("/api/auth/login", json=ACCOUNT)
    assert response.status_code == 200
    return response


def test_register_login_me_logout(client):
    registered = client.post("/api/auth/register", json=ACCOUNT)
    assert registered.status_code == 201
    assert set(registered.json()) == {"id", "email"}
    assert registered.json()["email"] == "persona@example.com"
    assert client.get("/api/auth/me").status_code == 401  # registro no inicia sesión
    logged = client.post("/api/auth/login", json=ACCOUNT)
    assert logged.status_code == 200
    assert client.get("/api/auth/me").json() == registered.json()
    headers = {"X-CSRF-Token": client.cookies.get(CSRF_COOKIE)}
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 204 and not response.content
    assert not client.cookies.get(SESSION_COOKIE)
    assert not client.cookies.get(CSRF_COOKIE)
    assert client.get("/api/auth/me").status_code == 401


def test_password_hash_and_duplicate_email(client, settings):
    registered = client.post("/api/auth/register", json=ACCOUNT)
    assert registered.status_code == 201
    with Session(client.app.state.engine) as session:
        user = session.scalar(select(User))
        assert user.password_hash.startswith("$argon2id$")
        assert ACCOUNT["password"] not in user.password_hash
        assert password_hasher.verify(user.password_hash, ACCOUNT["password"])
    duplicate = client.post(
        "/api/auth/register", json={**ACCOUNT, "email": " persona@example.com "}
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "email_exists"


@pytest.mark.parametrize(
    "email,password",
    [
        ("persona@example.com", "incorrecta"),
        ("nadie@example.com", "incorrecta"),
    ],
)
def test_bad_credentials_have_same_error(client, email, password):
    client.post("/api/auth/register", json=ACCOUNT)
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401
    assert response.json() == {
        "code": "invalid_credentials",
        "message": "Correo o contraseña incorrectos.",
    }
    assert not client.cookies.get(SESSION_COOKIE)


@pytest.mark.parametrize(
    "payload",
    [
        {**ACCOUNT, "email": "invalid"},
        {**ACCOUNT, "password": "corta"},
        {**ACCOUNT, "password": "x" * 129},
        {**ACCOUNT, "role": "admin"},
    ],
)
def test_validation_does_not_echo_secrets(client, payload):
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    assert payload["password"] not in response.text
    assert "input" not in response.text and "password_hash" not in response.text


def test_session_cookie_attributes_and_rotation(client):
    response = register_and_login(client)
    cookies = response.headers.get_list("set-cookie")
    session = next(c for c in cookies if c.startswith(SESSION_COOKIE))
    csrf = next(c for c in cookies if c.startswith(CSRF_COOKIE))
    assert "HttpOnly" in session and "SameSite=lax" in session and "Max-Age=28800" in session
    assert "HttpOnly" not in csrf
    assert response.headers["cache-control"] == "no-store"
    previous = client.cookies.get(SESSION_COOKIE)
    client.post("/api/auth/login", json=ACCOUNT)
    assert client.cookies.get(SESSION_COOKIE) != previous


def test_secure_cookies_with_https(settings):
    settings.cookie_secure = True
    with TestClient(create_app(settings), base_url="https://testserver") as client:
        response = register_and_login(client)
        assert all("Secure" in c for c in response.headers.get_list("set-cookie"))
        assert client.get("/api/auth/me").status_code == 200


@pytest.mark.parametrize("header", [None, "incorrecto", "no-ascii-é"])
def test_csrf_required(client, header):
    register_and_login(client)
    # Las cabeceras HTTP no permiten Unicode fuera de Latin-1/ASCII; usar bytes en ese caso.
    headers = {} if header is None else {"X-CSRF-Token": header.encode("utf-8")}
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 403
    assert response.json()["code"] == "csrf_invalid"
    assert client.get("/api/auth/me").status_code == 200


def test_matching_injected_csrf_cookie_and_header_is_rejected(client):
    register_and_login(client)
    original = client.cookies.get(CSRF_COOKIE)
    client.cookies.clear()
    # Restaurar una sesión válida, pero intentar sustituir el double-submit por otro valor.
    client.post("/api/auth/login", json=ACCOUNT)
    session = client.cookies.get(SESSION_COOKIE)
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, session)
    client.cookies.set(CSRF_COOKIE, original)
    assert client.post("/api/auth/logout", headers={"X-CSRF-Token": original}).status_code == 403


def test_sessions_cannot_be_forged_and_expire(client, settings):
    register_and_login(client)
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, "forged")
    assert client.get("/api/auth/me").status_code == 401
    signer = URLSafeTimedSerializer(
        settings.secret_key.get_secret_value(), salt="labtrack-session-v1"
    )
    with patch("itsdangerous.timed.time.time", return_value=datetime.now(UTC).timestamp() - 30000):
        expired = signer.dumps({"user_id": str(uuid4()), "csrf": "x"})
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, expired)
    assert client.get("/api/auth/me").status_code == 401


def test_missing_session_and_foreign_origin(client):
    assert client.post("/api/auth/logout").status_code == 401
    response = client.post(
        "/api/auth/register", json=ACCOUNT, headers={"Origin": "https://evil.example"}
    )
    assert response.status_code == 403
    register_and_login(client)
    response = client.post(
        "/api/auth/logout",
        headers={
            "Origin": "https://evil.example",
            "X-CSRF-Token": client.cookies.get(CSRF_COOKIE),
        },
    )
    assert response.status_code == 403


def test_registration_persists_across_app_restarts(client, settings):
    client.post("/api/auth/register", json=ACCOUNT)
    with TestClient(create_app(settings)) as restarted:
        assert restarted.post("/api/auth/login", json=ACCOUNT).status_code == 200
        assert restarted.get("/api/auth/me").json()["email"] == "persona@example.com"
