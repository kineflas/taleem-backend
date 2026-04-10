"""Add program categories + VOYELLES_SYLLABES curriculum type

Revision ID: 003
Revises: 002
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

_programcategory = postgresql.ENUM(
    "APPRENDRE_A_LIRE", "COMPRENDRE_ARABE", "CORAN",
    name="programcategory", create_type=False,
)


def upgrade() -> None:
    # 1. Create the new enum type
    _programcategory.create(op.get_bind(), checkfirst=True)

    # 2. Add VOYELLES_SYLLABES to the existing curriculumtype enum
    op.execute("ALTER TYPE curriculumtype ADD VALUE IF NOT EXISTS 'VOYELLES_SYLLABES'")

    # 3. Add category column with default
    op.add_column(
        "curriculum_programs",
        sa.Column(
            "category",
            _programcategory,
            nullable=False,
            server_default="APPRENDRE_A_LIRE",
        ),
    )

    # 4. Set correct categories for existing programs
    op.execute("""
        UPDATE curriculum_programs
        SET category = 'COMPRENDRE_ARABE'
        WHERE curriculum_type = 'MEDINE_T1'
    """)
    op.execute("""
        UPDATE curriculum_programs
        SET category = 'CORAN'
        WHERE curriculum_type IN ('TAJWID', 'HIFZ_REVISION')
    """)

    # 5. Remove server default (no longer needed)
    op.alter_column("curriculum_programs", "category", server_default=None)


def downgrade() -> None:
    op.drop_column("curriculum_programs", "category")
    _programcategory.drop(op.get_bind(), checkfirst=True)
    # Note: cannot remove enum value from curriculumtype in PostgreSQL
