"""init messaging schema

Revision ID: 00000001
Revises: 
Create Date: 2026-04-27 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = '00000001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create schema
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS messaging"))
    
    # Create outbox table
    op.create_table('outbox',
        sa.Column('aggregate_type', sa.String(), nullable=False),
        sa.Column('aggregate_id', sa.String(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('message_payload', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'DEAD_LETTERED', name='outbox_status_enum_messaging'), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='messaging'
    )
    op.create_index(op.f('ix_messaging_outbox_tenant_id'), 'outbox', ['tenant_id'], unique=False, schema='messaging')

def downgrade() -> None:
    op.drop_index(op.f('ix_messaging_outbox_tenant_id'), table_name='outbox', schema='messaging')
    op.drop_table('outbox', schema='messaging')
    op.execute(sa.text("DROP SCHEMA IF EXISTS messaging"))
