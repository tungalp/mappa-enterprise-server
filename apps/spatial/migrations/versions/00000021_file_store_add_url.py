"""file_store_add_url

Revision ID: 00000021
Revises: 00000020
Create Date: 2026-05-02 21:38:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00000021'
down_revision = '00000020'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add file_url column
    op.add_column('file_store', sa.Column('file_url', sa.String(), nullable=True), schema='spatial')
    
    # Drop file_data column
    op.drop_column('file_store', 'file_data', schema='spatial')

def downgrade() -> None:
    # Add file_data column back
    op.add_column('file_store', sa.Column('file_data', sa.LargeBinary(), nullable=True), schema='spatial')
               
    # Remove file_url column
    op.drop_column('file_store', 'file_url', schema='spatial')

