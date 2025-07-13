from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.api.api_service import ApiService

class ApiContainer(containers.DeclarativeContainer):
    """Api paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    api_service = providers.Factory(
        ApiService,
        async_db=database
    )
