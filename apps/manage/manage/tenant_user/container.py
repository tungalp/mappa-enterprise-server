from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.tenant_user.tenant_user_service import TenantUserService


class TenantUserContainer(containers.DeclarativeContainer):
    """Tenant konfigürasyonu"""

    database = providers.Dependency()

    tenant_user_service = providers.Factory(
        TenantUserService,
        async_db=database
    )