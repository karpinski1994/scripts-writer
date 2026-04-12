"""add_notebooklm_notebook_id_to_projects

Revision ID: f3e2758f1158
Revises: 9545cd70bf83
Create Date: 2026-04-12 17:23:02.150930

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3e2758f1158"
down_revision: Union[str, Sequence[str], None] = "9545cd70bf83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("projects", sa.Column("notebooklm_notebook_id", sa.String(length=100), nullable=True))
    with op.batch_alter_table("icp_profiles") as batch_op:
        batch_op.drop_constraint("ck_icp_profiles_source", type_="check")
        batch_op.create_check_constraint(
            "ck_icp_profiles_source",
            sa.text("source IN ('generated','uploaded','notebooklm')"),
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("icp_profiles") as batch_op:
        batch_op.drop_constraint("ck_icp_profiles_source", type_="check")
        batch_op.create_check_constraint(
            "ck_icp_profiles_source",
            sa.text("source IN ('generated','uploaded')"),
        )
    op.drop_column("projects", "notebooklm_notebook_id")
