"""empty message

Revision ID: bb9e31f8c628
Revises: 
Create Date: 2022-08-03 12:43:51.174287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb9e31f8c628'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('People')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('People',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"People_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('catchphrase', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='People_pkey')
    )
    # ### end Alembic commands ###
