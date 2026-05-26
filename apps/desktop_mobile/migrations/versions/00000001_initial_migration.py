"""Initial migration for desktop_mobile service

Revision ID: 00000001
Revises: None
Create Date: 2026-05-24 23:25:00.000000

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00000001'
down_revision = None
branch_labels = None
depends_on = None

SCHEMA_NAME = "desktop_mobile"

def upgrade() -> None:
    # 1. Create Schema
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
    
    # 2. Create collection table
    op.create_table(
        'collection',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('creator', sa.String(length=50), nullable=True),
        sa.Column('updater', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id', name='uq_collection_name_tenant'),
        schema=SCHEMA_NAME
    )
    op.create_index('ix_collection_tenant_id', 'collection', ['tenant_id'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_collection_name', 'collection', ['name'], unique=False, schema=SCHEMA_NAME)

    # 3. Create map table
    op.create_table(
        'map',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('project_file_url', sa.String(length=800), nullable=True),
        sa.Column('creator', sa.String(length=50), nullable=False),
        sa.Column('updater', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('web_map_id', sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA_NAME
    )
    op.create_index('ix_map_tenant_id', 'map', ['tenant_id'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_map_name', 'map', ['name'], unique=False, schema=SCHEMA_NAME)

    # 4. Create desktop_file_store table
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

    # 5. Create layer table
    op.create_table(
        'layer',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('tags', sa.String(length=255), nullable=True),
        sa.Column('url_path', sa.String(length=800), nullable=True),
        sa.Column('file_store_id', sa.Uuid(), nullable=True),
        sa.Column('qml_params', sa.JSON(), nullable=True),
        sa.Column('sld_params', sa.JSON(), nullable=True),
        sa.Column('creator', sa.String(length=50), nullable=False),
        sa.Column('updater', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('web_layer_definition_id', sa.Uuid(), nullable=True),
        sa.Column('bucket', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['file_store_id'], [f'{SCHEMA_NAME}.desktop_file_store.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA_NAME
    )
    op.create_index('ix_layer_tenant_id', 'layer', ['tenant_id'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_layer_name', 'layer', ['name'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_layer_file_store_id', 'layer', ['file_store_id'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_layer_web_layer_definition_id', 'layer', ['web_layer_definition_id'], unique=False, schema=SCHEMA_NAME)

    # 6. Create api_key table
    op.create_table(
        'api_key',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('public_lookup_id', sa.String(length=15), nullable=False),
        sa.Column('hashed_key', sa.String(length=128), nullable=False),
        sa.Column('description', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('public_lookup_id'),
        schema=SCHEMA_NAME
    )
    op.create_index('ix_api_key_tenant_id', 'api_key', ['tenant_id'], unique=False, schema=SCHEMA_NAME)
    op.create_index('ix_api_key_public_lookup_id', 'api_key', ['public_lookup_id'], unique=False, schema=SCHEMA_NAME)

    # 7. Create apikey_permission table
    op.create_table(
        'apikey_permission',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('apikey_id', sa.Uuid(), nullable=False),
        sa.Column('target_collection_id', sa.Uuid(), nullable=True),
        sa.Column('target_map_id', sa.Uuid(), nullable=True),
        sa.Column('target_layer_id', sa.Uuid(), nullable=True),
        sa.Column('access_level', sa.String(length=10), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('(target_collection_id IS NOT NULL)::int + (target_map_id IS NOT NULL)::int + (target_layer_id IS NOT NULL)::int <= 3', name='check_one_target_populated'),
        sa.ForeignKeyConstraint(['apikey_id'], [f'{SCHEMA_NAME}.api_key.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_collection_id'], [f'{SCHEMA_NAME}.collection.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_map_id'], [f'{SCHEMA_NAME}.map.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_layer_id'], [f'{SCHEMA_NAME}.layer.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA_NAME
    )
    op.create_index('ix_apikey_permission_tenant_id', 'apikey_permission', ['tenant_id'], unique=False, schema=SCHEMA_NAME)

    # 8. Create junction tables
    op.create_table(
        'collection_map',
        sa.Column('collection_id', sa.Uuid(), nullable=False),
        sa.Column('map_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], [f'{SCHEMA_NAME}.collection.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['map_id'], [f'{SCHEMA_NAME}.map.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('collection_id', 'map_id'),
        schema=SCHEMA_NAME
    )

    op.create_table(
        'map_layer',
        sa.Column('map_id', sa.Uuid(), nullable=False),
        sa.Column('layer_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['map_id'], [f'{SCHEMA_NAME}.map.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['layer_id'], [f'{SCHEMA_NAME}.layer.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('map_id', 'layer_id'),
        schema=SCHEMA_NAME
    )


def downgrade() -> None:
    op.drop_table('map_layer', schema=SCHEMA_NAME)
    op.drop_table('collection_map', schema=SCHEMA_NAME)
    op.drop_table('apikey_permission', schema=SCHEMA_NAME)
    op.drop_table('api_key', schema=SCHEMA_NAME)
    op.drop_table('layer', schema=SCHEMA_NAME)
    op.drop_table('desktop_file_store', schema=SCHEMA_NAME)
    op.drop_table('map', schema=SCHEMA_NAME)
    op.drop_table('collection', schema=SCHEMA_NAME)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE")
