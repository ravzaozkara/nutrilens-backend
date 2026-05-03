"""create base tables (original schema)

Revision ID: 0001
Revises:
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_diabetic", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_hypertensive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_high_cholesterol", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_celiac", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_kidney_disease", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "foods",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("calories", sa.Integer(), nullable=True),
        sa.Column("is_risky_for_diabetic", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_risky_for_hypertensive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_risky_for_cholesterol", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_risky_for_celiac", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("warning_message", sa.String(), nullable=True),
    )

    op.create_table(
        "meals",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("food_label", sa.String(), nullable=False),
        sa.Column("calories", sa.Float(), server_default="0"),
        sa.Column("protein", sa.Float(), server_default="0"),
        sa.Column("carbs", sa.Float(), server_default="0"),
        sa.Column("fat", sa.Float(), server_default="0"),
        sa.Column("health_warnings", sa.String(), server_default=""),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("meals")
    op.drop_table("foods")
    op.drop_table("users")
