from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.route.route_service import RouteService

class RouteContainer(containers.DeclarativeContainer):
    """Route paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    route_service = providers.Factory(
        RouteService,
        async_db=database
    )
