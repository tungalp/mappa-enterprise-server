from dependency_injector import containers, providers
from mapa.spatial.connection.connection_service import ConnectionService


class ConnectionContainer(containers.DeclarativeContainer):
    """Connection paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    connection_service = providers.Factory(
        ConnectionService,
        async_db=database,
    )
