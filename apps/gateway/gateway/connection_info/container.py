from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService

class ConnectionInfoContainer(containers.DeclarativeContainer):
    """ConnectionInfo paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    connection_info_service = providers.Factory(
        ConnectionInfoService,
        async_db=database
    )
