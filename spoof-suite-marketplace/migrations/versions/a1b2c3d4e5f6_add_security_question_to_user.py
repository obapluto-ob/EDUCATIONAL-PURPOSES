"""add security question to user

Revision ID: a1b2c3d4e5f6
Revises: 2c1142bb8a10
Create Date: 2026-10-06 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '2c1142bb8a10'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('user', sa.Column('security_question', sa.String(255), nullable=True))
    except Exception:
        pass
    try:
        op.add_column('user', sa.Column('security_answer', sa.String(512), nullable=True))
    except Exception:
        pass


def downgrade():
    try:
        op.drop_column('user', 'security_question')
        op.drop_column('user', 'security_answer')
    except Exception:
        pass
