from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from mapa.gateway.context_var.context_var_service import ContextVarService
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from service.root.root_service import RootService


class RootContainer(containers.DeclarativeContainer):
    """Root paketinin bağımlılık konteyneri"""

    database = providers.Dependency()
    messenger = providers.Dependency()

    gateway_api_service = providers.Factory(
        GatewayApiService, async_db=database, messenger=messenger
    )

    connection_info_service = providers.Singleton(
        ConnectionInfoService, async_db=database
    )

    context_var_service = providers.Singleton(ContextVarService, async_db=database)

    root_service = providers.Singleton(
        RootService,
        async_db=database,
        gateway_api_service=gateway_api_service,
        connection_info_service=connection_info_service,
        context_var_service=context_var_service,
        messenger=messenger
    )
