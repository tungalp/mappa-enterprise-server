from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.client_api_scope.client_api_scope_service import ClientApiScopeService

class ClientApiScopeContainer(containers.DeclarativeContainer):
    """ClientApiScope paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    client_api_scope_service = providers.Factory(
        ClientApiScopeService,
        async_db=database
    )
