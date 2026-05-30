"""Add summary and entities to events table

Revision ID: 20260530212746
Revises: 20260530201813_create_events_table
Create Date: 2026-05-30 21:27:46

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260530212746'
down_revision = '20260530201813_create_events_table'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('events', sa.Column('summary', sa.Text, nullable=True))
    op.add_column('events', sa.Column('entities', sa.Text, nullable=True))


def downgrade():
    op.drop_column('events', 'entities')
    op.drop_column('events', 'summary')
