from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.api_scope.api_scope_service import ApiScopeService

class ApiScopeContainer(containers.DeclarativeContainer):
    """ApiScope paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    api_scope_service = providers.Factory(
        ApiScopeService,
        async_db=database
    )
