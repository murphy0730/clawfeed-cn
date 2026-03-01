"""Authentication routes — WeChat login + JWT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.deps import get_db, get_current_user
from app.models import User
from app import crud
from app.schemas import WechatLoginRequest, UserOut
from app.services.wechat import code2session

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def _create_jwt(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expire_days)
    return jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _user_dict(u: User) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "avatar": u.avatar,
        "slug": u.slug,
    }


@router.get("/config")
async def auth_config():
    """Tell the frontend which auth methods are available."""
    return {
        "wechatEnabled": bool(settings.wechat_appid and settings.wechat_secret),
    }


@router.post("/login")
async def wechat_login(
    data: WechatLoginRequest,
    db: Session = Depends(get_db),
):
    """WeChat Mini-Program login: exchange code for openid → upsert user → JWT."""
    wx_resp = await code2session(data.code)
    openid = wx_resp["openid"]

    user = crud.get_user_by_openid(db, openid)
    if not user:
        user = crud.create_user(
            db,
            openid=openid,
            name=data.nickname,
            avatar=data.avatar_url,
        )

    token = _create_jwt({"sub": str(user.id), "openid": openid})
    return {"token": token, "user": _user_dict(user)}


@router.post("/dev-login")
async def dev_login(db: Session = Depends(get_db)):
    """Development-only: auto-create/login a test user without WeChat.
    Disabled when WECHAT_APPID is configured.
    """
    if settings.wechat_appid:
        raise HTTPException(status_code=403, detail="dev login disabled in production")
    user = crud.get_user_by_openid(db, "dev-user")
    if not user:
        user = crud.create_user(
            db,
            openid="dev-user",
            name="Dev User",
        )
    token = _create_jwt({"sub": str(user.id), "openid": "dev-user"})
    return {"token": token, "user": _user_dict(user)}


@router.get("/me")
async def get_me(user: User | None = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="not authenticated")
    return {"user": _user_dict(user)}


@router.post("/logout")
async def logout():
    """JWT is stateless — client just discards the token."""
    return {"ok": True}
