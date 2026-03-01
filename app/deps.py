"""FastAPI dependencies — DB session, current user, API-key verification."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generator

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session as SASession

from app.config import get_settings
from app.database import SessionLocal
from app.models import User

settings = get_settings()


def get_db() -> Generator[SASession, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("exp") and datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc):
            return None
        return payload
    except JWTError:
        return None


def get_current_user(
    authorization: str | None = Header(None),
    db: SASession = Depends(get_db),
) -> User | None:
    """Return the logged-in user or None (non-strict)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    payload = _decode_token(token)
    if not payload or "sub" not in payload:
        return None
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    return user


def require_user(
    user: User | None = Depends(get_current_user),
) -> User:
    """Raise 401 if not authenticated."""
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    return user


def verify_api_key(
    authorization: str | None = Header(None),
) -> str:
    """Verify Bearer token matches the configured API_KEY."""
    if not settings.api_key:
        raise HTTPException(status_code=401, detail="API key not configured")
    bearer = ""
    if authorization and authorization.startswith("Bearer "):
        bearer = authorization[7:]
    if bearer != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid api key")
    return bearer
