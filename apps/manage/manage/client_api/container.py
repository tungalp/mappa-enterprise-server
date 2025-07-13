from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.client_api.client_api_service import ClientApiService

class ClientApiContainer(containers.DeclarativeContainer):
    """ClientApi paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    client_api_service = providers.Factory(
        ClientApiService,
        async_db=database
    )
