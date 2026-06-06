"""Add layer_groups column to map table

Revision ID: 00000003
Revises: 00000002
Create Date: 2026-06-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '00000003'
down_revision = '00000002'
branch_labels = None
depends_on = None

SCHEMA_NAME = "desktop_mobile"

def upgrade() -> None:
    op.add_column('map', sa.Column('layer_groups', sa.JSON(), nullable=True), schema=SCHEMA_NAME)

def downgrade() -> None:
    op.drop_column('map', 'layer_groups', schema=SCHEMA_NAME)
