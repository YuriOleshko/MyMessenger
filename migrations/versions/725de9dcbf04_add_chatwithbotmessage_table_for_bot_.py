"""Add ChatWithBotMessage table for bot chat

Revision ID: 725de9dcbf04
Revises: 81eb7aff4184
Create Date: 2024-11-06 21:19:06.238481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '725de9dcbf04'
down_revision = '81eb7aff4184'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_with_bot_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('bot_response', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_with_bot_message')
    # ### end Alembic commands ###
