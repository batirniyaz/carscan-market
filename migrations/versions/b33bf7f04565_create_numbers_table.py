"""create numbers table

Revision ID: b33bf7f04565
Revises: 8fadef4abc94
Create Date: 2024-09-08 21:43:17.566147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b33bf7f04565'
down_revision: Union[str, None] = '8fadef4abc94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('number',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('number', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='number_pkey')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('car',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('number', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('date', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('time', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('image_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='car_pkey')
    )
    op.create_index('ix_car_id', 'car', ['id'], unique=False)
    # ### end Alembic commands ###
