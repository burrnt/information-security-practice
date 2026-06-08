"""add audit_log table

Revision ID: 504aa8bb1165
Revises: 221f17b282a6
Create Date: 2026-06-08 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '504aa8bb1165'
down_revision: Union[str, None] = '221f17b282a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Створюємо тільки таблицю audit_log, ігноруючи обмеження SQLite
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('http_method', sa.String(length=10), nullable=True),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_action_ts', 'audit_log', ['action', 'timestamp'], unique=False)
    op.create_index('ix_audit_ip_action', 'audit_log', ['ip_address', 'action'], unique=False)
    op.create_index('ix_audit_user_ts', 'audit_log', ['user_id', 'timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_audit_user_ts', table_name='audit_log')
    op.drop_index('ix_audit_ip_action', table_name='audit_log')
    op.drop_index('ix_audit_action_ts', table_name='audit_log')
    op.drop_table('audit_log')