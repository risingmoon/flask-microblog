"""empty message

Revision ID: 56c120a684e1
Revises: 158d7120d5f6
Create Date: 2014-03-13 13:55:38.051291

"""

# revision identifiers, used by Alembic.
revision = '56c120a684e1'
down_revision = '158d7120d5f6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], )
    )
    op.drop_column(u'post', 'category_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'post', sa.Column('category_id', sa.INTEGER(), nullable=True))
    op.drop_table('categories')
    ### end Alembic commands ###
