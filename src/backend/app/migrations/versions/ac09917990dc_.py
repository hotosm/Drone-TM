"""

Revision ID: ac09917990dc
Revises: 62a16e505bc3
Create Date: 2024-07-04 10:52:52.166220

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ac09917990dc"
down_revision: Union[str, None] = "62a16e505bc3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("projects", "dem_url", existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("projects", "dem_url", existing_type=sa.VARCHAR(), nullable=False)
    # ### end Alembic commands ###