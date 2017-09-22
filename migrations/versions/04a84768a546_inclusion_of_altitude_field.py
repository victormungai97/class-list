"""inclusion of altitude field

Revision ID: 04a84768a546
Revises: f4a8ef2b6155
Create Date: 2017-09-22 23:36:04.003049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04a84768a546'
down_revision = 'f4a8ef2b6155'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('extras', sa.Column('altitude', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('extras', 'altitude')
    # ### end Alembic commands ###
