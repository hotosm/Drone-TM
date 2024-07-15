"""refine field name

Revision ID: acee47666167
Revises: 88ae62ec8876
Create Date: 2024-07-13 10:51:33.020864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "acee47666167"
down_revision: Union[str, None] = "88ae62ec8876"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("projects", sa.Column("created_at", sa.DateTime(), nullable=False))
    op.add_column("projects", sa.Column("deadline_at", sa.DateTime(), nullable=True))
    op.drop_column("projects", "created")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "projects",
        sa.Column(
            "created", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("projects", "deadline_at")
    op.drop_column("projects", "created_at")
    # ### end Alembic commands ###
