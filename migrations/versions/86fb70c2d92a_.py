"""empty message

Revision ID: 86fb70c2d92a
Revises: a083f3670d53
Create Date: 2020-07-10 12:41:51.001195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86fb70c2d92a'
down_revision = 'a083f3670d53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('completed', sa.Boolean(), nullable=True))

    op.execute('UPDATE todos SET completed = False WHERE completed IS NULL;')

    op.alter_column('todos', 'completed', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todos', 'completed')
    # ### end Alembic commands ###
