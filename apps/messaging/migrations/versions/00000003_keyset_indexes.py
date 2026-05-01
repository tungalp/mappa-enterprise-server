"""add keyset pagination indexes

Revision ID: 00000003
Revises: 00000002
Create Date: 2026-04-27 18:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00000003'
down_revision = '00000002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Index for keyset pagination in rooms
    op.create_index(
        'ix_messaging_message_room_id_id_desc',
        'message',
        ['room_id', sa.text('id DESC')],
        schema='messaging'
    )
    
    # Index for keyset pagination in DMs
    op.create_index(
        'ix_messaging_message_receiver_sender_id_desc',
        'message',
        ['receiver_id', 'sender_id', sa.text('id DESC')],
        schema='messaging'
    )

def downgrade() -> None:
    op.drop_index('ix_messaging_message_receiver_sender_id_desc', table_name='message', schema='messaging')
    op.drop_index('ix_messaging_message_room_id_id_desc', table_name='message', schema='messaging')
