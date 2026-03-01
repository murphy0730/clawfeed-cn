"""Add raw_items table for content fetching pipeline.

Revision ID: 002_add_raw_items
Revises: 001_init
Create Date: 2026-03-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_add_raw_items"
down_revision: Union[str, None] = "001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "raw_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), server_default="", nullable=True),
        sa.Column("url", sa.Text(), server_default="", nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("content", sa.Text(), server_default="", nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("dedup_key", sa.String(255), nullable=False),
        sa.Column("metadata", sa.Text(), server_default="{}", nullable=True),
        sa.Column("is_used", sa.Integer(), server_default="0", nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("source_id", "dedup_key", name="uq_source_dedup"),
    )
    op.create_index("idx_raw_items_fetched", "raw_items", [sa.text("fetched_at DESC")])
    op.create_index("idx_raw_items_used", "raw_items", ["is_used"])
    op.create_index("idx_raw_items_source", "raw_items", ["source_id"])


def downgrade() -> None:
    op.drop_index("idx_raw_items_source", table_name="raw_items")
    op.drop_index("idx_raw_items_used", table_name="raw_items")
    op.drop_index("idx_raw_items_fetched", table_name="raw_items")
    op.drop_table("raw_items")
