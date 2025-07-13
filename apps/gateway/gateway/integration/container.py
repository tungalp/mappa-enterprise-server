from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from mapa.gateway.integration.integration_service import IntegrationService
from mapa.gateway.route.route_service import RouteService

class IntegrationContainer(containers.DeclarativeContainer):
    """Integration paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
        
    route_service = providers.Factory(
        RouteService,
        async_db=database
    )
    
    connection_info_service = providers.Factory(
        ConnectionInfoService,
        async_db=database
    )
        
        
    integration_service = providers.Factory(
        IntegrationService,
        async_db=database,
        route_service=route_service,
        connection_info_service=connection_info_service
    )
