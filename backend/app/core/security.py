import secrets
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, Request, Response
from itsdangerous import BadData, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.errors import APIError
from backend.app.models import User

SESSION_COOKIE = "labtrack_session"
CSRF_COOKIE = "labtrack_csrf"
CSRF_HEADER = "X-CSRF-Token"
password_hasher = PasswordHasher()
_dummy_hash = password_hasher.hash(secrets.token_urlsafe(32))


def serializer(request: Request) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        request.app.state.settings.secret_key.get_secret_value(), salt="labtrack-session-v1"
    )


def ensure_same_origin(request: Request):
    origin = request.headers.get("origin")
    expected = f"{request.url.scheme}://{request.url.netloc}"
    if origin and origin != expected:
        raise APIError(403, "origin_invalid", "El origen de la solicitud no está permitido.")


def issue_session(request: Request, response: Response, user: User):
    settings = request.app.state.settings
    csrf = secrets.token_urlsafe(32)
    token = serializer(request).dumps({"user_id": str(user.id), "csrf": csrf})
    options = dict(
        max_age=settings.session_ttl_seconds,
        path="/",
        secure=settings.cookie_secure,
        samesite="lax",
    )
    response.set_cookie(SESSION_COOKIE, token, httponly=True, **options)
    response.set_cookie(CSRF_COOKIE, csrf, httponly=False, **options)


def clear_session(request: Request, response: Response):
    secure = request.app.state.settings.cookie_secure
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, secure=secure, samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", httponly=False, secure=secure, samesite="lax")


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    try:
        if not token:
            raise ValueError("missing")
        payload = serializer(request).loads(
            token, max_age=request.app.state.settings.session_ttl_seconds
        )
        user_id = UUID(payload["user_id"])
        if not isinstance(payload["csrf"], str) or not payload["csrf"]:
            raise ValueError("csrf")
    except (BadData, ValueError, KeyError, TypeError):
        raise APIError(401, "unauthenticated", "Inicia sesión para continuar.") from None
    user = db.get(User, user_id)
    if user is None:
        raise APIError(401, "unauthenticated", "Inicia sesión para continuar.")
    request.state.session_payload = payload
    return user


def require_csrf(request: Request, user: User = Depends(current_user)) -> User:
    ensure_same_origin(request)
    expected = request.state.session_payload["csrf"]
    cookie = request.cookies.get(CSRF_COOKIE, "")
    header = request.headers.get(CSRF_HEADER, "")
    # double-submit unido a la sesión firmada: igualar cookie y header no basta.
    try:
        valid = secrets.compare_digest(cookie, expected) and secrets.compare_digest(
            header, expected
        )
    except TypeError:
        valid = False
    if not valid:
        raise APIError(
            403, "csrf_invalid", "La validación de seguridad falló. Inicia sesión de nuevo."
        )
    return user


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        password_hasher.verify(password_hash or _dummy_hash, password)
        return password_hash is not None
    except (VerificationError, InvalidHashError):
        return False
