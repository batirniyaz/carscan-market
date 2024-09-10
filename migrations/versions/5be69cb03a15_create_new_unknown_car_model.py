"""create new unknown car model

Revision ID: 5be69cb03a15
Revises: cc10b4b3e62a
Create Date: 2024-09-10 18:59:34.120696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5be69cb03a15'
down_revision: Union[str, None] = 'cc10b4b3e62a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('unknown_car',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('number', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('date', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('time', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('image_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='unknown_car_pkey')
    )
    op.create_index('ix_unknown_car_id', 'unknown_car', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_unknown_car_id', table_name='unknown_car')
    op.drop_table('unknown_car')
    # ### end Alembic commands ###