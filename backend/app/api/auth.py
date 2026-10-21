from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.security import (
    clear_session,
    current_user,
    ensure_same_origin,
    issue_session,
    password_hasher,
    require_csrf,
    verify_password,
)
from backend.app.db import get_db
from backend.app.errors import APIError
from backend.app.models import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    ensure_same_origin(request)
    user = User(
        email=str(data.email), password_hash=password_hasher.hash(data.password.get_secret_value())
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise APIError(409, "email_exists", "Ya existe una cuenta con ese correo.") from None
    db.refresh(user)
    return user


@router.post("/login", response_model=UserResponse)
def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    ensure_same_origin(request)
    user = db.scalar(select(User).where(User.email == str(data.email)))
    if not verify_password(data.password.get_secret_value(), user.password_hash if user else None):
        raise APIError(401, "invalid_credentials", "Correo o contraseña incorrectos.")
    if password_hasher.check_needs_rehash(user.password_hash):
        user.password_hash = password_hasher.hash(data.password.get_secret_value())
        db.commit()
    issue_session(request, response, user)
    return user


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)):
    return user


@router.post("/logout", status_code=204)
def logout(request: Request, user: User = Depends(require_csrf)):
    response = Response(status_code=204)
    clear_session(request, response)
    return response
