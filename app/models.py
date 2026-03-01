"""SQLAlchemy ORM models — mirrors the 9 migration files."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(
        String,
        CheckConstraint("type IN ('4h','daily','weekly','monthly')"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", Text, default="{}")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_digests_type", "type"),
        Index("idx_digests_created", created_at.desc()),
        Index("idx_digests_user", "user_id"),
    )


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    title = Column(Text, default="")
    note = Column(Text, default="")
    status = Column(
        String,
        CheckConstraint("status IN ('pending','processed')"),
        nullable=False,
        default="pending",
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_marks_status", "status"),
        Index("idx_marks_url", "url"),
    )


class Config(Base):
    __tablename__ = "config"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_id = Column(String, unique=True, nullable=True)
    openid = Column(String, unique=True, nullable=True, index=True)
    unionid = Column(String, nullable=True)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    slug = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    marks = relationship("Mark", backref="user", lazy="dynamic")
    subscriptions = relationship("UserSubscription", backref="user", lazy="dynamic")

    __table_args__ = (Index("idx_users_slug", "slug", unique=True),)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    config = Column(Text, nullable=False, default="{}")
    is_active = Column(Integer, default=1)
    is_public = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    last_fetched_at = Column(DateTime, nullable=True)
    fetch_count = Column(Integer, default=0)
    is_deleted = Column(Integer, default=0)
    deleted_at = Column(DateTime, nullable=True)

    creator = relationship("User", backref="sources", foreign_keys=[created_by])

    __table_args__ = (
        Index("idx_sources_type", "type"),
        Index("idx_sources_active", "is_active"),
        Index("idx_sources_created_by", "created_by"),
    )


class SourcePack(Base):
    __tablename__ = "source_packs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    slug = Column(String, unique=True)
    sources_json = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_public = Column(Integer, default=1)
    install_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    creator = relationship("User", backref="packs", foreign_keys=[created_by])


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    source_id = Column(
        Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    source = relationship("Source", backref="subscriptions", foreign_keys=[source_id])

    __table_args__ = (
        UniqueConstraint("user_id", "source_id", name="uq_user_source"),
        Index("idx_user_subs_user", "user_id"),
        Index("idx_user_subs_source", "source_id"),
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    reply = Column(Text, nullable=True)
    replied_by = Column(String, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    status = Column(String, default="open")
    category = Column(String, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="feedback", foreign_keys=[user_id])

    __table_args__ = (
        Index("idx_feedback_user", "user_id"),
        Index("idx_feedback_status", "status"),
    )


class RawItem(Base):
    __tablename__ = "raw_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(
        Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(Text, default="")
    url = Column(Text, default="")
    author = Column(String, nullable=True)
    content = Column(Text, default="")
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, nullable=False, server_default=func.now())
    dedup_key = Column(String(255), nullable=False)
    metadata_ = Column("metadata", Text, default="{}")
    is_used = Column(Integer, default=0)  # 0=未使用, 1=已入 digest

    source = relationship("Source", backref="raw_items", foreign_keys=[source_id])

    __table_args__ = (
        UniqueConstraint("source_id", "dedup_key", name="uq_source_dedup"),
        Index("idx_raw_items_fetched", fetched_at.desc()),
        Index("idx_raw_items_used", "is_used"),
        Index("idx_raw_items_source", "source_id"),
    )
