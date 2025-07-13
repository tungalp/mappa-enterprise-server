from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.tenant.tenant_service import TenantService
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.manage.tenant_client.tenant_client_service import TenantClientService


class TenantContainer(containers.DeclarativeContainer):
    """Tenant konfigürasyonu"""

    database = providers.Dependency()

    tenant_service = providers.Factory(
        TenantService,
        async_db=database
    )

    tenant_user_service = providers.Factory(
        TenantUserService,
        async_db=database
    )

    tenant_client_service = providers.Factory(
        TenantClientService,
        async_db=database
    )