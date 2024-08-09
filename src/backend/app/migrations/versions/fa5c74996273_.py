"""

Revision ID: fa5c74996273
Revises: ac09917990dc
Create Date: 2024-07-05 11:51:02.146671

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fa5c74996273"
down_revision: Union[str, None] = "ac09917990dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the existing enum type
existing_taskstatus_enum = sa.Enum(
    "READY",
    "LOCKED_FOR_MAPPING",
    "MAPPED",
    "LOCKED_FOR_VALIDATION",
    "VALIDATED",
    "INVALIDATED",
    "BAD",
    "SPLIT",
    name="taskstatus",
)

# Define the new enum type
new_state_enum = sa.Enum(
    "UNLOCKED_TO_MAP",
    "LOCKED_FOR_MAPPING",
    "UNLOCKED_TO_VALIDATE",
    "LOCKED_FOR_VALIDATION",
    "UNLOCKED_DONE",
    name="state",
)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Create the new enum type in the database
    new_state_enum.create(op.get_bind())

    # Use the USING clause to convert existing column values to the new enum type
    op.execute(
        "ALTER TABLE task_events ALTER COLUMN state TYPE state USING state::text::state"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Use the USING clause to convert back to the original enum type
    op.execute(
        "ALTER TABLE task_events ALTER COLUMN state TYPE taskstatus USING state::text::taskstatus"
    )

    # Drop the new enum type from the database
    new_state_enum.drop(op.get_bind())
    # ### end Alembic commands ###