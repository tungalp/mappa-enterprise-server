"""qgis_plugin_client

Revision ID: 00000022
Revises: 00000021
Create Date: 2026-05-25 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import date

# revision identifiers, used by Alembic.
revision = '00000022'
down_revision = '00000021'
branch_labels = None
depends_on = None


def upgrade() -> None:
    meta = sa.MetaData()
    client_table = sa.Table('client', meta, schema='manage', autoload_with=op.get_bind())
    tenant_client_table = sa.Table('tenant_client', meta, schema='manage', autoload_with=op.get_bind())
    client_api_table = sa.Table('client_api', meta, schema='manage', autoload_with=op.get_bind())

    # Insert QGIS Plugin client
    op.bulk_insert(
        client_table,
        [
            {
                'id': "9be5c4d6-84ba-40bb-b150-409e339e5b66",
                'created_at': date(2026, 5, 25),
                'name': "qgis_plugin",
                'client_id': "client_id_qgis_plugin",
                'client_secret': "QgisPluginSecretKey123",
                'grant_types': ["authorization_code", "refresh_token", "client_credentials"],
                'redirect_uris': [
                    "http://localhost:8787",
                    "http://localhost:8787/"
                ],
                'application_type': "native",
                'require_consent': True,
                'is_system': True,
                'require_pkce': True,
                'level_type': "FIRST_PARTY",
            }
        ]
    )

    # Insert tenant client mapping (associate with Admin tenant)
    op.bulk_insert(
        tenant_client_table,
        [
            {
                'id': "902e2038-acd1-4736-9a5a-f45e159b2d99",
                'created_at': date(2026, 5, 25),
                'tenant_id': "10a2238f-4d1e-4626-9f3c-799d3ef5e96d",
                'client_id': "9be5c4d6-84ba-40bb-b150-409e339e5b66"
            }
        ]
    )

    # Insert client api mapping (give access to Workspace Api)
    op.bulk_insert(
        client_api_table,
        [
            {
                'id': "2285466f-7071-4b1f-875a-a712d48cbefa",
                'created_at': date(2026, 5, 25),
                'tenant_id': "00000000-0000-0000-0000-000000000000",
                'api_id': "fe379bb7-2275-4b29-823b-da8a616b2cbe", # Workspace Api
                'client_id': "9be5c4d6-84ba-40bb-b150-409e339e5b66"
            }
        ]
    )


def downgrade() -> None:
    meta = sa.MetaData()
    client_table = sa.Table('client', meta, schema='manage', autoload_with=op.get_bind())
    tenant_client_table = sa.Table('tenant_client', meta, schema='manage', autoload_with=op.get_bind())
    client_api_table = sa.Table('client_api', meta, schema='manage', autoload_with=op.get_bind())

    op.execute("DELETE FROM manage.client_api WHERE client_id = '9be5c4d6-84ba-40bb-b150-409e339e5b66'")
    op.execute("DELETE FROM manage.tenant_client WHERE client_id = '9be5c4d6-84ba-40bb-b150-409e339e5b66'")
    op.execute("DELETE FROM manage.client WHERE id = '9be5c4d6-84ba-40bb-b150-409e339e5b66'")
