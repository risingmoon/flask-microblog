"""empty message

Revision ID: 158d7120d5f6
Revises: 3574bab9b15
Create Date: 2014-03-13 13:44:26.500907

"""

# revision identifiers, used by Alembic.
revision = '158d7120d5f6'
down_revision = '3574bab9b15'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'post', sa.Column('category_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'post', 'category_id')
    op.drop_table('category')
    ### end Alembic commands ###