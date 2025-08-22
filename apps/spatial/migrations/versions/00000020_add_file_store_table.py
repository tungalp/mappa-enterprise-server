"""add_file_store_table

Revision ID: 00000020
Revises: 00000019
Create Date: 2025-08-19 12:30:00.000000
"""
from alembic import op
import sqlalchemy_utils
import sqlalchemy as sa
from datetime import date
from datetime import datetime
from sqlalchemy_utils import UUIDType


from mapa.core.data.base_entity import NULL_TENANT_ID

# revision identifiers, used by Alembic.
revision = '00000020'
down_revision = '00000019'
branch_labels = None
depends_on = None


table_list = [
    "file_store"
]

def upgrade() -> None:
    op.create_table(
        'file_store',
        sa.Column('id', UUIDType(binary=False), primary_key=True, nullable=False),
        sa.Column('creator_user_id', UUIDType(binary=False), nullable=True),
        sa.Column('updater_user_id', UUIDType(binary=False), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('file_format', sa.String(length=10), nullable=False),
        sa.Column('file_data', sa.LargeBinary(), nullable=False),
        sa.Column('tenant_id', UUIDType(binary=False), nullable=False, index=True),
        # sa.UniqueConstraint('file_data', 'tenant_id', name='spatial_file_store_uk_1'),
        schema='spatial'
    )

    # tenant_isolation
    execute_tenant_isolation("spatial", table_list, enable=True)

def downgrade() -> None:
    op.drop_table('file_store', schema='spatial')

    # tenant_isolation
    down_list = table_list.copy()
    down_list.reverse()
    execute_tenant_isolation("spatial", down_list, enable=False)

def execute_tenant_isolation(schema, tables, enable):
    for table in tables:
        full_name = f"{schema}.{table}"
        if enable:
            op.execute( f"alter table {full_name} enable row level security")
            op.execute( f"create policy tenant_isolation_insert on {full_name} "
                        f"for INSERT "
                        f"WITH CHECK (current_setting('app.tenant_id') is not null and (select true from (select pg_typeof(uuid(current_setting('app.tenant_id')))::text as typ) s where s.typ = 'uuid'))"
                        )
            op.execute( f"create policy tenant_isolation_select on {full_name} "
                        f"for SELECT "
                        f"using  ((current_setting('app.tenant_id') = tenant_id::text) OR ((tenant_id)::text = '{str(NULL_TENANT_ID)}'))"
                        )
            op.execute( f"create policy tenant_isolation_update on {full_name} "
                        f"for UPDATE "
                        f"using  ((current_setting('app.tenant_id') = tenant_id::text)) "
                        f"WITH CHECK (current_setting('app.tenant_id') is not null and (select true from (select pg_typeof(uuid(current_setting('app.tenant_id')))::text as typ) s where s.typ = 'uuid'))"
                        )
            op.execute( f"create policy tenant_isolation_delete on {full_name} "
                        f"for DELETE "
                        f"using  ((current_setting('app.tenant_id') = tenant_id::text))"
                        )
        else:
            op.execute(f"drop policy tenant_isolation_insert on {full_name}")
            op.execute(f"drop policy tenant_isolation_select on {full_name}")
            op.execute(f"drop policy tenant_isolation_update on {full_name}")
            op.execute(f"drop policy tenant_isolation_delete on {full_name}")
            op.execute(f"alter table {full_name} disable row level security")