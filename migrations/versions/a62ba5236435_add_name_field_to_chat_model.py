"""Add name field to Chat model

Revision ID: a62ba5236435
Revises: 4e4cea6a387e
Create Date: 2024-11-06 15:06:52.112053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a62ba5236435'
down_revision = '4e4cea6a387e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###