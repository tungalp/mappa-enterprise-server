from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.tenant_client.tenant_client_service import TenantClientService


class TenantClientContainer(containers.DeclarativeContainer):
    """Tenant konfigürasyonu"""

    database = providers.Dependency()

    tenant_client_service = providers.Factory(
        TenantClientService,
        async_db=database
    )
    