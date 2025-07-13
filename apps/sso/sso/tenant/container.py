from dependency_injector import containers
from dependency_injector import providers

class TenantContainer(containers.DeclarativeContainer):
    """Tenant konfigürasyonu"""

    messenger = providers.Dependency()