"""add recovery_key and firesale table

Revision ID: e9f1a2b3c4d5
Revises: d7dc8cad6bd1
Create Date: 2026-10-06 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e9f1a2b3c4d5'
down_revision = 'd7dc8cad6bd1'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    user_cols = [c['name'] for c in inspector.get_columns('user')]
    tables = inspector.get_table_names()

    with op.batch_alter_table('user', schema=None) as batch_op:
        if 'recovery_key_hash' not in user_cols:
            batch_op.add_column(sa.Column('recovery_key_hash', sa.String(512), nullable=True))

    if 'fire_sale' not in tables:
        op.create_table(
            'fire_sale',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('discount_percent', sa.Integer(), nullable=False),
            sa.Column('duration_minutes', sa.Integer(), nullable=False),
            sa.Column('started_at', sa.DateTime(), nullable=False),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    op.drop_table('fire_sale')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('recovery_key_hash')
