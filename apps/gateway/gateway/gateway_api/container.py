from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService

class GatewayApiContainer(containers.DeclarativeContainer):
    """GatewayApi paketinin bağımlılık konteyneri"""

    database = providers.Dependency()
    gateway_util_service = providers.Dependency()
    messenger = providers.Dependency()

    gateway_api_service = providers.Factory(
        GatewayApiService, async_db=database, messenger=messenger
    )
