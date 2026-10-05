"""increase password_hash length

Revision ID: 2c1142bb8a10
Revises: 66bcd8cf2fbd
Create Date: 2026-10-06 01:04:14.278697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c1142bb8a10'
down_revision = '66bcd8cf2fbd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'credit_card',
        sa.Column('validity_percent', sa.Integer(), nullable=True),
    )
    op.alter_column(
        'user',
        'password_hash',
        existing_type=sa.VARCHAR(length=128),
        type_=sa.String(length=512),
        existing_nullable=True,
    )


def downgrade():
    op.drop_column('credit_card', 'validity_percent')
