"""add materia_id to mentors

Revision ID: 8c46aa0e0fc2
Revises: 6e9fb6c7cd1e
Create Date: 2026-05-22 13:26:44.488005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c46aa0e0fc2'
down_revision: Union[str, Sequence[str], None] = '6e9fb6c7cd1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
      """Upgrade schema."""
      with op.batch_alter_table("mentors") as batch_op:
          batch_op.add_column(sa.Column("materia_id", sa.Integer(), nullable=True))
          batch_op.create_foreign_key(
              "fk_mentors_materia_id",
              "materias",
              ["materia_id"],
              ["id"],
              ondelete="SET NULL",
          )


def downgrade() -> None:
      """Downgrade schema."""
      with op.batch_alter_table("mentors") as batch_op:
          batch_op.drop_constraint("fk_mentors_materia_id", type_="foreignkey")
          batch_op.drop_column("materia_id")
