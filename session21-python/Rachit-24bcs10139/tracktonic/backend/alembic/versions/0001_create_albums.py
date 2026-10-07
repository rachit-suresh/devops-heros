"""create albums table
Revision ID: 0001_create_albums
Revises:
Create Date: 2026-10-07
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_albums"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "albums",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("artist", sa.String(200), nullable=False),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("albums")
