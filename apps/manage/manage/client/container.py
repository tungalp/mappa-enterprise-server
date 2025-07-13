from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.client.client_service import ClientService


class ClientContainer(containers.DeclarativeContainer):
    """Client paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    client_api_service = providers.Dependency()
    tenant_client_service = providers.Dependency()
    
    client_service = providers.Factory(
        ClientService,
        async_db=database,
        tenant_client_service=tenant_client_service,
        client_api_service=client_api_service
    )
