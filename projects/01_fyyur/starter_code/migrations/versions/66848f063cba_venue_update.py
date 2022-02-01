"""Venue update

Revision ID: 66848f063cba
Revises: 3f6696e8f4d5
Create Date: 2022-01-25 22:04:01.974394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66848f063cba'
down_revision = '3f6696e8f4d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String(length=120)), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'genres')
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###
