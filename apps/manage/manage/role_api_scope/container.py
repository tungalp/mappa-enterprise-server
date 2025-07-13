from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.role_api_scope.role_api_scope_service import RoleApiScopeService

class RoleApiScopeContainer(containers.DeclarativeContainer):
    """RoleApiScope paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    role_api_scope_service = providers.Factory(
        RoleApiScopeService,
        async_db=database
    )
