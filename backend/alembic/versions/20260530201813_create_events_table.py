"""Create events table

Revision ID: 20260530201813
Revises: 
Create Date: 2026-05-30 20:18:13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260530201813'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'events',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('text', sa.Text, index=True),
        sa.Column('source_type', sa.String(50)),
        sa.Column('source_id', sa.String(255), index=True),
        sa.Column('credibility_score', sa.Float, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table('events')
