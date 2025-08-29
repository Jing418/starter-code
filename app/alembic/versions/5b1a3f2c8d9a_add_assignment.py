"""add assignment

Revision ID: 5b1a3f2c8d9a
Revises: 2dcfc2ce13cb
Create Date: 2025-08-29 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b1a3f2c8d9a"
down_revision: Union[str, Sequence[str], None] = "2dcfc2ce13cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add assignment table."""
    op.create_table(
        "assignment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("submission_date", sa.DateTime(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["classroom_id"], ["classroom.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["user_account.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignment_id"), "assignment", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema by dropping assignment table."""
    op.drop_index(op.f("ix_assignment_id"), table_name="assignment")
    op.drop_table("assignment")

