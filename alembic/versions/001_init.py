"""Initial schema — consolidated from Node.js migrations 001-009.

Revision ID: 001_init
Revises:
Create Date: 2026-02-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # digests
    op.create_table(
        "digests",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", sa.Text, server_default="{}"),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("type IN ('4h','daily','weekly','monthly')"),
    )
    op.create_index("idx_digests_type", "digests", ["type"])
    op.create_index("idx_digests_created", "digests", [sa.text("created_at DESC")])
    op.create_index("idx_digests_user", "digests", ["user_id"])

    # marks
    op.create_table(
        "marks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("title", sa.Text, server_default=""),
        sa.Column("note", sa.Text, server_default=""),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('pending','processed')"),
    )
    op.create_index("idx_marks_status", "marks", ["status"])
    op.create_index("idx_marks_url", "marks", ["url"])

    # config
    op.create_table(
        "config",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", sa.Text, nullable=False),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("google_id", sa.String, unique=True, nullable=True),
        sa.Column("openid", sa.String, unique=True, nullable=True),
        sa.Column("unionid", sa.String, nullable=True),
        sa.Column("email", sa.String, nullable=True),
        sa.Column("name", sa.String, nullable=True),
        sa.Column("avatar", sa.String, nullable=True),
        sa.Column("slug", sa.String, unique=True, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_users_slug", "users", ["slug"], unique=True)

    # sessions
    op.create_table(
        "sessions",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )

    # sources
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("config", sa.Text, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Integer, server_default="1"),
        sa.Column("is_public", sa.Integer, server_default="0"),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_fetched_at", sa.DateTime, nullable=True),
        sa.Column("fetch_count", sa.Integer, server_default="0"),
        sa.Column("is_deleted", sa.Integer, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )
    op.create_index("idx_sources_type", "sources", ["type"])
    op.create_index("idx_sources_active", "sources", ["is_active"])
    op.create_index("idx_sources_created_by", "sources", ["created_by"])

    # source_packs
    op.create_table(
        "source_packs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("slug", sa.String, unique=True),
        sa.Column("sources_json", sa.Text, nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_public", sa.Integer, server_default="1"),
        sa.Column("install_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # user_subscriptions
    op.create_table(
        "user_subscriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_active", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "source_id", name="uq_user_source"),
    )
    op.create_index("idx_user_subs_user", "user_subscriptions", ["user_id"])
    op.create_index("idx_user_subs_source", "user_subscriptions", ["source_id"])

    # feedback
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("email", sa.String, nullable=True),
        sa.Column("name", sa.String, nullable=True),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("reply", sa.Text, nullable=True),
        sa.Column("replied_by", sa.String, nullable=True),
        sa.Column("replied_at", sa.DateTime, nullable=True),
        sa.Column("status", sa.String, server_default="open"),
        sa.Column("category", sa.String, nullable=True),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("idx_feedback_user", "feedback", ["user_id"])
    op.create_index("idx_feedback_status", "feedback", ["status"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("user_subscriptions")
    op.drop_table("source_packs")
    op.drop_table("sources")
    op.drop_table("sessions")
    op.drop_table("users")
    op.drop_table("config")
    op.drop_table("marks")
    op.drop_table("digests")
