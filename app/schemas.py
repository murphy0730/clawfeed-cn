"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Auth ──


class WechatLoginRequest(BaseModel):
    code: str
    nickname: str | None = None
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    token: str
    user: UserOut


class UserOut(BaseModel):
    id: int
    name: str | None = None
    email: str | None = None
    avatar: str | None = None
    slug: str | None = None

    model_config = {"from_attributes": True}


# ── Digests ──


class DigestCreate(BaseModel):
    type: str
    content: str
    metadata: str = "{}"
    created_at: str | None = None


class DigestOut(BaseModel):
    id: int
    type: str
    content: str
    metadata: str | None = Field(None, alias="metadata_")
    created_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


# ── Marks ──


class MarkCreate(BaseModel):
    url: str
    title: str = ""
    note: str = ""


class MarkLegacyCreate(BaseModel):
    url: str


class MarkOut(BaseModel):
    id: int
    url: str
    title: str | None = None
    note: str | None = None
    status: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Sources ──


class SourceCreate(BaseModel):
    name: str
    type: str
    config: str = "{}"
    isPublic: bool = False


class SourceUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    config: str | None = None
    isActive: bool | None = None
    isPublic: bool | None = None


class SourceResolveRequest(BaseModel):
    url: str


class SourceOut(BaseModel):
    id: int
    name: str
    type: str
    config: str | None = None
    is_active: int | None = None
    is_public: int | None = None
    created_by: int | None = None
    creator_name: str | None = None
    created_at: datetime | None = None
    subscribed: bool | None = None

    model_config = {"from_attributes": True}


# ── Subscriptions ──


class SubscribeRequest(BaseModel):
    sourceId: int


class BulkSubscribeRequest(BaseModel):
    sourceIds: list[int]


# ── Packs ──


class PackCreate(BaseModel):
    name: str
    description: str = ""
    slug: str | None = None
    sourcesJson: str | None = None
    sources_json: str | None = None


class PackOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    slug: str | None = None
    sources: list[Any] = []
    created_by: int | None = None
    creator_name: str | None = None
    creator_avatar: str | None = None
    creator_slug: str | None = None
    is_public: int | None = None
    install_count: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Feedback ──


class FeedbackCreate(BaseModel):
    message: str
    email: str | None = None
    name: str | None = None
    category: str | None = None


class FeedbackReply(BaseModel):
    reply: str
    replied_by: str = "agent"


class FeedbackStatusUpdate(BaseModel):
    status: str


# ── Config ──


class ConfigUpdate(BaseModel):
    """Arbitrary key-value pairs."""

    model_config = {"extra": "allow"}
