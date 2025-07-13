from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.context_var.context_var_service import ContextVarService

class ContextVarContainer(containers.DeclarativeContainer):
    """ContextVar paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    context_var_service = providers.Factory(
        ContextVarService,
        async_db=database
    )
