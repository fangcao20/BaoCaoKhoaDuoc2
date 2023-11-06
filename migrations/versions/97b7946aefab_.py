"""empty message

Revision ID: 97b7946aefab
Revises: dc53418077c3
Create Date: 2023-10-28 18:47:53.059542

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '97b7946aefab'
down_revision = 'dc53418077c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('import_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dot_thau_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('import_history_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'dot_thau', ['dot_thau_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.drop_column('code')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('import_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('import_history_ibfk_2', 'dot_thau', ['code'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.drop_column('dot_thau_id')

    # ### end Alembic commands ###