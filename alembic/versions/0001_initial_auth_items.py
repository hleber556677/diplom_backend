"""initial academy tables

Revision ID: 0001_initial_auth_items
Revises:
Create Date: 2026-04-22 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_auth_items"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "module_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_slug", sa.String(length=100), nullable=False),
        sa.Column("best_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("earned_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_module_progress_id"), "module_progress", ["id"], unique=False)
    op.create_index(
        op.f("ix_module_progress_module_slug"),
        "module_progress",
        ["module_slug"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_module_progress_module_slug"), table_name="module_progress")
    op.drop_index(op.f("ix_module_progress_id"), table_name="module_progress")
    op.drop_table("module_progress")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
