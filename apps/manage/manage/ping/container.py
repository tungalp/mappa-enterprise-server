from dependency_injector import containers
from dependency_injector import providers


class PingContainer(containers.DeclarativeContainer):
    """Ping paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
