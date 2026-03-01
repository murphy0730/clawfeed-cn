"""CRUD operations — ports every exported function from db.mjs."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models import (
    Config,
    Digest,
    Feedback,
    Mark,
    RawItem,
    Source,
    SourcePack,
    User,
    UserSubscription,
)


# ── helpers ──


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _generate_slug(email: str | None, name: str | None) -> str:
    base = ((email or "").split("@")[0] if email else (name or "user")).lower()
    return re.sub(r"[^a-z0-9_-]", "", base)[:30] or "user"


# ── Digests ──


def list_digests(
    db: Session,
    *,
    type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Digest]:
    q = db.query(Digest)
    if type:
        q = q.filter(Digest.type == type)
    return q.order_by(Digest.created_at.desc()).offset(offset).limit(limit).all()


def get_digest(db: Session, digest_id: int) -> Digest | None:
    return db.query(Digest).filter(Digest.id == digest_id).first()


def create_digest(
    db: Session,
    *,
    type: str,
    content: str,
    metadata: str = "{}",
    created_at: str | None = None,
) -> Digest:
    d = Digest(type=type, content=content, metadata_=metadata)
    if created_at:
        d.created_at = created_at
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ── Marks ──


def list_marks(
    db: Session,
    *,
    user_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Mark]:
    q = db.query(Mark)
    if user_id is not None:
        q = q.filter(Mark.user_id == user_id)
    if status:
        q = q.filter(Mark.status == status)
    return q.order_by(Mark.created_at.desc()).offset(offset).limit(limit).all()


def create_mark(
    db: Session,
    *,
    url: str,
    user_id: int,
    title: str = "",
    note: str = "",
) -> dict:
    existing = (
        db.query(Mark).filter(Mark.url == url, Mark.user_id == user_id).first()
    )
    if existing:
        return {"id": existing.id, "duplicate": True}
    m = Mark(url=url, title=title, note=note, user_id=user_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id, "duplicate": False}


def delete_mark(db: Session, mark_id: int, user_id: int) -> None:
    db.query(Mark).filter(Mark.id == mark_id, Mark.user_id == user_id).delete()
    db.commit()


# ── Users / Auth ──


def get_user_by_openid(db: Session, openid: str) -> User | None:
    return db.query(User).filter(User.openid == openid).first()


def get_user_by_google_id(db: Session, google_id: str) -> User | None:
    return db.query(User).filter(User.google_id == google_id).first()


def get_user_by_slug(db: Session, slug: str) -> User | None:
    return db.query(User).filter(User.slug == slug).first()


def _ensure_unique_slug(db: Session, slug: str, exclude_id: int | None = None) -> str:
    candidate = slug
    i = 1
    while True:
        q = db.query(User).filter(User.slug == candidate)
        if exclude_id is not None:
            q = q.filter(User.id != exclude_id)
        if q.first() is None:
            return candidate
        candidate = f"{slug}{i}"
        i += 1


def create_user(
    db: Session,
    *,
    openid: str | None = None,
    google_id: str | None = None,
    email: str | None = None,
    name: str | None = None,
    avatar: str | None = None,
) -> User:
    slug = _ensure_unique_slug(db, _generate_slug(email, name))
    u = User(
        openid=openid,
        google_id=google_id,
        email=email,
        name=name,
        avatar=avatar,
        slug=slug,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    # Auto-subscribe to public sources
    auto_subscribe_public_sources(db, u.id)
    return u


def upsert_user_by_google(
    db: Session,
    *,
    google_id: str,
    email: str,
    name: str,
    avatar: str,
) -> User:
    existing = get_user_by_google_id(db, google_id)
    if existing:
        existing.email = email
        existing.name = name
        existing.avatar = avatar
        if not existing.slug:
            existing.slug = _ensure_unique_slug(
                db, _generate_slug(email, name), exclude_id=existing.id
            )
        db.commit()
        db.refresh(existing)
        return existing
    return create_user(
        db, google_id=google_id, email=email, name=name, avatar=avatar
    )


def auto_subscribe_public_sources(db: Session, user_id: int) -> None:
    public_sources = db.query(Source).filter(Source.is_public == 1).all()
    for s in public_sources:
        existing = (
            db.query(UserSubscription)
            .filter(
                UserSubscription.user_id == user_id,
                UserSubscription.source_id == s.id,
            )
            .first()
        )
        if not existing:
            db.add(UserSubscription(user_id=user_id, source_id=s.id))
    db.commit()


# ── Feed ──


def list_digests_by_user(
    db: Session,
    user_id: int,
    *,
    type: str | None = None,
    limit: int = 10,
    since: str | None = None,
) -> list[Digest]:
    q = db.query(Digest).filter(
        (Digest.user_id == user_id) | (Digest.user_id.is_(None))
    )
    if type:
        q = q.filter(Digest.type == type)
    if since:
        q = q.filter(Digest.created_at >= since)
    return q.order_by(Digest.created_at.desc()).limit(min(limit, 50)).all()


def count_digests_by_user(
    db: Session,
    user_id: int,
    *,
    type: str | None = None,
) -> int:
    q = db.query(func.count(Digest.id)).filter(
        (Digest.user_id == user_id) | (Digest.user_id.is_(None))
    )
    if type:
        q = q.filter(Digest.type == type)
    return q.scalar() or 0


# ── Sources ──


def list_sources(
    db: Session,
    *,
    user_id: int | None = None,
    include_public: bool = False,
    active_only: bool = False,
) -> list[dict]:
    q = db.query(Source, User.name.label("creator_name")).outerjoin(
        User, Source.created_by == User.id
    )
    conditions = [Source.is_deleted == 0]
    if active_only:
        conditions.append(Source.is_active == 1)
    if user_id and include_public:
        conditions.append((Source.created_by == user_id) | (Source.is_public == 1))
    elif user_id:
        conditions.append(Source.created_by == user_id)
    elif include_public:
        conditions.append(Source.is_public == 1)
    q = q.filter(*conditions).order_by(Source.created_at.desc())
    results = []
    for source, creator_name in q.all():
        d = {c.name: getattr(source, c.name) for c in source.__table__.columns}
        d["creator_name"] = creator_name
        results.append(d)
    return results


def get_source(db: Session, source_id: int) -> Source | None:
    return db.query(Source).filter(Source.id == source_id).first()


def create_source(
    db: Session,
    *,
    name: str,
    type: str,
    config: str = "{}",
    is_public: bool = False,
    created_by: int | None = None,
) -> Source:
    s = Source(
        name=name,
        type=type,
        config=config,
        is_public=1 if is_public else 0,
        created_by=created_by,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    # Auto-subscribe creator
    if created_by:
        existing = (
            db.query(UserSubscription)
            .filter(
                UserSubscription.user_id == created_by,
                UserSubscription.source_id == s.id,
            )
            .first()
        )
        if not existing:
            db.add(UserSubscription(user_id=created_by, source_id=s.id))
            db.commit()
    return s


def update_source(db: Session, source_id: int, patch: dict) -> None:
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        return
    allowed_map = {
        "name": "name",
        "type": "type",
        "config": "config",
        "is_active": "is_active",
        "isActive": "is_active",
        "is_public": "is_public",
        "isPublic": "is_public",
    }
    for key, val in patch.items():
        col = allowed_map.get(key)
        if col:
            if isinstance(val, bool):
                val = 1 if val else 0
            setattr(s, col, val)
    s.updated_at = _utcnow()
    db.commit()


def delete_source(db: Session, source_id: int, user_id: int | None = None) -> None:
    q = db.query(Source).filter(Source.id == source_id)
    if user_id:
        q = q.filter(Source.created_by == user_id)
    s = q.first()
    if s:
        s.is_deleted = 1
        s.deleted_at = _utcnow()
        db.commit()


def get_source_by_type_config(db: Session, type: str, config: str) -> Source | None:
    return (
        db.query(Source).filter(Source.type == type, Source.config == config).first()
    )


# ── Source Packs ──


def create_pack(
    db: Session,
    *,
    name: str,
    description: str = "",
    slug: str,
    sources_json: str,
    created_by: int,
) -> SourcePack:
    p = SourcePack(
        name=name,
        description=description,
        slug=slug,
        sources_json=sources_json,
        created_by=created_by,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def get_pack(db: Session, pack_id: int) -> SourcePack | None:
    return db.query(SourcePack).filter(SourcePack.id == pack_id).first()


def get_pack_by_slug(db: Session, slug: str) -> dict | None:
    row = (
        db.query(
            SourcePack,
            User.name.label("creator_name"),
            User.avatar.label("creator_avatar"),
            User.slug.label("creator_slug"),
        )
        .outerjoin(User, SourcePack.created_by == User.id)
        .filter(SourcePack.slug == slug)
        .first()
    )
    if not row:
        return None
    pack, creator_name, creator_avatar, creator_slug = row
    d = {c.name: getattr(pack, c.name) for c in pack.__table__.columns}
    d["creator_name"] = creator_name
    d["creator_avatar"] = creator_avatar
    d["creator_slug"] = creator_slug
    return d


def list_packs(
    db: Session,
    *,
    public_only: bool = False,
    user_id: int | None = None,
) -> list[dict]:
    q = db.query(
        SourcePack,
        User.name.label("creator_name"),
        User.avatar.label("creator_avatar"),
        User.slug.label("creator_slug"),
    ).outerjoin(User, SourcePack.created_by == User.id)
    if public_only and user_id:
        q = q.filter(
            (SourcePack.is_public == 1) | (SourcePack.created_by == user_id)
        )
    elif public_only:
        q = q.filter(SourcePack.is_public == 1)
    elif user_id:
        q = q.filter(SourcePack.created_by == user_id)
    q = q.order_by(SourcePack.install_count.desc(), SourcePack.created_at.desc())
    results = []
    for pack, creator_name, creator_avatar, creator_slug in q.all():
        d = {c.name: getattr(pack, c.name) for c in pack.__table__.columns}
        d["creator_name"] = creator_name
        d["creator_avatar"] = creator_avatar
        d["creator_slug"] = creator_slug
        results.append(d)
    return results


def increment_pack_install(db: Session, pack_id: int) -> None:
    p = db.query(SourcePack).filter(SourcePack.id == pack_id).first()
    if p:
        p.install_count = (p.install_count or 0) + 1
        p.updated_at = _utcnow()
        db.commit()


def delete_pack(db: Session, pack_id: int) -> None:
    db.query(SourcePack).filter(SourcePack.id == pack_id).delete()
    db.commit()


# ── Subscriptions ──


def list_subscriptions(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(
            Source,
            UserSubscription.created_at.label("subscribed_at"),
            User.name.label("creator_name"),
        )
        .join(UserSubscription, UserSubscription.source_id == Source.id)
        .outerjoin(User, Source.created_by == User.id)
        .filter(UserSubscription.user_id == user_id)
        .order_by(UserSubscription.created_at.desc())
        .all()
    )
    results = []
    for source, subscribed_at, creator_name in rows:
        d = {c.name: getattr(source, c.name) for c in source.__table__.columns}
        d["subscribed_at"] = subscribed_at
        d["creator_name"] = creator_name
        results.append(d)
    return results


def subscribe(db: Session, user_id: int, source_id: int) -> None:
    existing = (
        db.query(UserSubscription)
        .filter(
            UserSubscription.user_id == user_id,
            UserSubscription.source_id == source_id,
        )
        .first()
    )
    if not existing:
        db.add(UserSubscription(user_id=user_id, source_id=source_id))
        db.commit()


def unsubscribe(db: Session, user_id: int, source_id: int) -> None:
    db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.source_id == source_id,
    ).delete()
    db.commit()


def bulk_subscribe(db: Session, user_id: int, source_ids: list[int]) -> int:
    added = 0
    for sid in source_ids:
        existing = (
            db.query(UserSubscription)
            .filter(
                UserSubscription.user_id == user_id,
                UserSubscription.source_id == sid,
            )
            .first()
        )
        if not existing:
            db.add(UserSubscription(user_id=user_id, source_id=sid))
            added += 1
    db.commit()
    return added


def is_subscribed(db: Session, user_id: int, source_id: int) -> bool:
    return (
        db.query(UserSubscription)
        .filter(
            UserSubscription.user_id == user_id,
            UserSubscription.source_id == source_id,
        )
        .first()
        is not None
    )


# ── Feedback ──


def create_feedback(
    db: Session,
    user_id: int | None,
    email: str | None,
    name: str | None,
    message: str,
    category: str | None = None,
) -> int:
    f = Feedback(
        user_id=user_id,
        email=email,
        name=name,
        message=message,
        category=category,
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f.id


def get_user_feedback(db: Session, user_id: int) -> list[Feedback]:
    return (
        db.query(Feedback)
        .filter(Feedback.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


def get_all_feedback(db: Session) -> list[dict]:
    rows = (
        db.query(
            Feedback,
            User.name.label("user_name"),
            User.email.label("user_email"),
            User.avatar.label("user_avatar"),
        )
        .outerjoin(User, Feedback.user_id == User.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    results = []
    for fb, user_name, user_email, user_avatar in rows:
        d = {c.name: getattr(fb, c.name) for c in fb.__table__.columns}
        d["user_name"] = user_name
        d["user_email"] = user_email
        d["user_avatar"] = user_avatar
        results.append(d)
    return results


def reply_to_feedback(
    db: Session, feedback_id: int, reply: str, replied_by: str = "agent"
) -> None:
    f = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if f:
        f.reply = reply
        f.replied_by = replied_by
        f.replied_at = _utcnow()
        f.status = "replied"
        db.commit()


def update_feedback_status(db: Session, feedback_id: int, status: str) -> None:
    f = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if f:
        f.status = status
        db.commit()


def mark_feedback_read(db: Session, feedback_id: int) -> None:
    f = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if f:
        f.read_at = _utcnow()
        db.commit()


def mark_all_feedback_read(db: Session, user_id: int) -> None:
    db.query(Feedback).filter(
        Feedback.user_id == user_id,
        Feedback.reply.isnot(None),
        Feedback.read_at.is_(None),
    ).update({"read_at": _utcnow()})
    db.commit()


def get_unread_feedback_count(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(Feedback.id))
        .filter(
            Feedback.user_id == user_id,
            Feedback.reply.isnot(None),
            Feedback.read_at.is_(None),
        )
        .scalar()
        or 0
    )


# ── Config ──


def get_config(db: Session) -> dict:
    rows = db.query(Config).all()
    result = {}
    for r in rows:
        try:
            result[r.key] = json.loads(r.value)
        except (json.JSONDecodeError, TypeError):
            result[r.key] = r.value
    return result


def set_config(db: Session, key: str, value) -> None:
    v = value if isinstance(value, str) else json.dumps(value)
    existing = db.query(Config).filter(Config.key == key).first()
    if existing:
        existing.value = v
    else:
        db.add(Config(key=key, value=v))
    db.commit()


# ── Raw Items ──


def get_unused_raw_items(
    db: Session,
    *,
    since: datetime,
    source_types: list[str] | None = None,
    limit: int = 200,
) -> list[RawItem]:
    q = db.query(RawItem).filter(
        RawItem.is_used == 0,
        RawItem.fetched_at >= since,
    )
    if source_types:
        q = q.join(Source, RawItem.source_id == Source.id).filter(
            Source.type.in_(source_types)
        )
    return q.order_by(RawItem.fetched_at.desc()).limit(limit).all()


def mark_items_used(db: Session, item_ids: list[int]) -> None:
    if not item_ids:
        return
    db.query(RawItem).filter(RawItem.id.in_(item_ids)).update(
        {"is_used": 1}, synchronize_session=False
    )
    db.commit()


def list_active_sources_by_types(
    db: Session, types: list[str]
) -> list[Source]:
    return (
        db.query(Source)
        .filter(
            Source.is_active == 1,
            Source.is_deleted == 0,
            Source.type.in_(types),
        )
        .all()
    )
