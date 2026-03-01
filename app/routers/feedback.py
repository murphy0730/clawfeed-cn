"""Feedback routes."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session

from app.config import get_settings
from app.deps import get_db, get_current_user, require_user, verify_api_key
from app.models import User
from app import crud
from app.schemas import FeedbackCreate, FeedbackReply, FeedbackStatusUpdate

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
settings = get_settings()


def _check_api_key(authorization: str | None, key: str | None) -> None:
    """Accept API key via query param or Bearer header."""
    bearer = ""
    if authorization and authorization.startswith("Bearer "):
        bearer = authorization[7:]
    if not settings.api_key or (key != settings.api_key and bearer != settings.api_key):
        raise HTTPException(status_code=401, detail="invalid api key")


@router.post("")
async def create_feedback(
    data: FeedbackCreate,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = (data.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message required")
    fb_id = crud.create_feedback(
        db,
        user_id=user.id if user else None,
        email=data.email,
        name=data.name,
        message=message,
        category=data.category,
    )
    # Lark notification (fire-and-forget)
    if settings.feedback_lark_webhook:
        user_name = (user.name if user else data.name) or "Anonymous"
        user_email = (user.email if user else data.email) or ""
        from datetime import datetime, timezone

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        text = (
            f"\U0001f4e8 \u65b0\u53cd\u9988 #{fb_id}\n"
            f"\U0001f464 {user_name}"
            f"{' (' + user_email + ')' if user_email else ''}\n"
            f'\U0001f4ac "{message[:200]}"\n'
            f"\U0001f550 {now_str}"
        )
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    settings.feedback_lark_webhook,
                    json={"msg_type": "text", "content": {"text": text}},
                    timeout=5.0,
                )
        except Exception:
            pass
    return {"ok": True, "id": fb_id}


@router.get("")
async def get_feedback(
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user:
        return []
    feedback = crud.get_user_feedback(db, user.id)
    unread = crud.get_unread_feedback_count(db, user.id)
    return {
        "feedback": [
            {
                "id": f.id,
                "message": f.message,
                "reply": f.reply,
                "replied_by": f.replied_by,
                "replied_at": f.replied_at,
                "created_at": f.created_at,
                "status": f.status,
                "category": f.category,
                "read_at": f.read_at,
            }
            for f in feedback
        ],
        "unread": unread,
    }


@router.post("/read")
async def mark_read(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    crud.mark_all_feedback_read(db, user.id)
    return {"ok": True}


@router.get("/all")
async def get_all_feedback(
    key: str | None = None,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    _check_api_key(authorization, key)
    return crud.get_all_feedback(db)


@router.post("/{feedback_id}/reply")
async def reply_feedback(
    feedback_id: int,
    data: FeedbackReply,
    key: str | None = None,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    _check_api_key(authorization, key)
    crud.reply_to_feedback(db, feedback_id, data.reply, data.replied_by)
    return {"ok": True}


@router.patch("/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: int,
    data: FeedbackStatusUpdate,
    key: str | None = None,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    _check_api_key(authorization, key)
    valid = {"open", "auto_draft", "needs_human", "replied", "closed"}
    if data.status not in valid:
        raise HTTPException(status_code=400, detail="invalid status")
    crud.update_feedback_status(db, feedback_id, data.status)
    return {"ok": True}
