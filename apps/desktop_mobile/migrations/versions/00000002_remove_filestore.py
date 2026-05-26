"""Remove desktop_file_store and file_store_id from layer

Revision ID: 00000002
Revises: 00000001
Create Date: 2026-05-25 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00000002'
down_revision = '00000001'
branch_labels = None
depends_on = None

SCHEMA_NAME = "desktop_mobile"

def upgrade() -> None:
    # 1. Drop foreign key constraint on layer
    op.drop_constraint('layer_file_store_id_fkey', 'layer', schema=SCHEMA_NAME, type_='foreignkey')
    
    # 2. Drop index ix_layer_file_store_id
    op.drop_index('ix_layer_file_store_id', table_name='layer', schema=SCHEMA_NAME)
    
    # 3. Drop column file_store_id from layer
    op.drop_column('layer', 'file_store_id', schema=SCHEMA_NAME)
    
    # 4. Drop desktop_file_store table
    op.drop_table('desktop_file_store', schema=SCHEMA_NAME)


def downgrade() -> None:
    # 1. Re-create desktop_file_store table
    op.create_table(
        'desktop_file_store',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('file_url', sa.String(length=800), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('creator', sa.String(length=50), nullable=False),
        sa.Column('updater', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA_NAME
    )
    op.create_index('ix_desktop_file_store_tenant_id', 'desktop_file_store', ['tenant_id'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_desktop_file_store_file_hash', 'desktop_file_store', ['file_hash'], unique=False, schema=SCHEMA_NAME)

    # 2. Re-add file_store_id column to layer
    op.add_column('layer', sa.Column('file_store_id', sa.Uuid(), nullable=True), schema=SCHEMA_NAME)
    
    # 3. Re-create index ix_layer_file_store_id
    op.create_index('ix_layer_file_store_id', 'layer', ['file_store_id'], unique=False, schema=SCHEMA_NAME)
    
    # 4. Re-create foreign key constraint
    op.create_foreign_key(
        'layer_file_store_id_fkey',
        'layer',
        'desktop_file_store',
        ['file_store_id'],
        ['id'],
        source_schema=SCHEMA_NAME,
        referent_schema=SCHEMA_NAME,
        ondelete='SET NULL'
    )
