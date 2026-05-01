"""create messaging tables

Revision ID: 00000002
Revises: 00000001
Create Date: 2026-04-27 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '00000002'
down_revision = '00000001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Room table
    op.create_table('room',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('foto', sa.String(), nullable=True),
        sa.Column('creator_user_id', sa.Uuid(), nullable=True),
        sa.Column('updater_user_id', sa.Uuid(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='messaging'
    )
    
    # Room Users table
    op.create_table('room_users',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('room_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['messaging.room.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='messaging'
    )
    op.create_index(op.f('ix_messaging_room_users_tenant_id'), 'room_users', ['tenant_id'], unique=False, schema='messaging')
    
    # Message table
    op.create_table('message',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('sender_id', sa.Uuid(), nullable=False),
        sa.Column('receiver_id', sa.Uuid(), nullable=True),
        sa.Column('room_id', sa.Uuid(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('read1_at', sa.DateTime(), nullable=True),
        sa.Column('read2_at', sa.DateTime(), nullable=True),
        sa.Column('creator_user_id', sa.Uuid(), nullable=True),
        sa.Column('updater_user_id', sa.Uuid(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['messaging.room.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='messaging'
    )
    
    # Message Files table
    op.create_table('message_files',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('message_id', sa.Uuid(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=False),
        sa.Column('data_hash', sa.String(), nullable=True),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messaging.message.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='messaging'
    )
    
    # Signal table
    op.create_table('signal',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('layer', sa.String(), nullable=False),
        sa.Column('geom', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromText', name='geometry'), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='messaging'
    )
    op.create_index(op.f('ix_messaging_signal_entity_id'), 'signal', ['entity_id'], unique=False, schema='messaging')
    op.create_index(op.f('ix_messaging_signal_layer'), 'signal', ['layer'], unique=False, schema='messaging')

def downgrade() -> None:
    op.drop_index(op.f('ix_messaging_signal_layer'), table_name='signal', schema='messaging')
    op.drop_index(op.f('ix_messaging_signal_entity_id'), table_name='signal', schema='messaging')
    op.drop_table('signal', schema='messaging')
    op.drop_table('message_files', schema='messaging')
    op.drop_table('message', schema='messaging')
    op.drop_index(op.f('ix_messaging_room_users_tenant_id'), table_name='room_users', schema='messaging')
    op.drop_table('room_users', schema='messaging')
    op.drop_table('room', schema='messaging')
