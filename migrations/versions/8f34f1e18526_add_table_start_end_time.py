"""add table start_end_time

Revision ID: 8f34f1e18526
Revises: 5ee95176e825
Create Date: 2024-09-13 17:52:25.566572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f34f1e18526'
down_revision: Union[str, None] = '5ee95176e825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.create_table('start_end_time',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('start_time', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('end_time', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='start_end_time_pkey')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('start_end_time')
    op.drop_index('ix_start_end_time_id', table_name='start_end_time')
    # ### end Alembic commands ###
