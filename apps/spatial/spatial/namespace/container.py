from dependency_injector import containers, providers
from mapa.spatial.namespace.namespace_service import NamespaceService


class NamespaceContainer(containers.DeclarativeContainer):
    """Namespace paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    namespace_service = providers.Factory(
        NamespaceService,
        async_db=database,
    )
