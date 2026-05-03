"""add user profile fields; drop is_high_cholesterol and is_celiac

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-23

Changes:
  - ADD: name, birth_date, gender, height_cm, weight_kg (profile)
  - ADD: daily_calorie_goal, protein_goal, carbs_goal, fat_goal (nutrition goals)
  - DROP: is_high_cholesterol (reduced health-condition set per project spec)
  - DROP: is_celiac          (reduced health-condition set per project spec)
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Drop retired health-condition columns ──────────────────────────────────
    op.drop_column("users", "is_high_cholesterol")
    op.drop_column("users", "is_celiac")

    # ── Add profile fields ─────────────────────────────────────────────────────
    op.add_column("users", sa.Column("name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("birth_date", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("gender", sa.String(), nullable=True))
    op.add_column("users", sa.Column("height_cm", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("weight_kg", sa.Float(), nullable=True))

    # ── Add nutrition-goal columns (with DB-level defaults) ───────────────────
    # TODO: compute per-user via Mifflin-St Jeor once height/weight/age/gender available
    op.add_column("users", sa.Column(
        "daily_calorie_goal", sa.Float(), nullable=False, server_default="2000"
    ))
    op.add_column("users", sa.Column(
        "protein_goal", sa.Float(), nullable=False, server_default="90"
    ))
    op.add_column("users", sa.Column(
        "carbs_goal", sa.Float(), nullable=False, server_default="250"
    ))
    op.add_column("users", sa.Column(
        "fat_goal", sa.Float(), nullable=False, server_default="70"
    ))


def downgrade() -> None:
    # ── Remove nutrition-goal columns ─────────────────────────────────────────
    op.drop_column("users", "fat_goal")
    op.drop_column("users", "carbs_goal")
    op.drop_column("users", "protein_goal")
    op.drop_column("users", "daily_calorie_goal")

    # ── Remove profile fields ─────────────────────────────────────────────────
    op.drop_column("users", "weight_kg")
    op.drop_column("users", "height_cm")
    op.drop_column("users", "gender")
    op.drop_column("users", "birth_date")
    op.drop_column("users", "name")

    # ── Re-add retired health-condition columns ────────────────────────────────
    op.add_column("users", sa.Column(
        "is_high_cholesterol", sa.Boolean(), nullable=False, server_default="false"
    ))
    op.add_column("users", sa.Column(
        "is_celiac", sa.Boolean(), nullable=False, server_default="false"
    ))
