from dependency_injector import containers, providers
from mapa.spatial.reference.reference_service import ReferenceService


class ReferenceContainer(containers.DeclarativeContainer):
    """Reference paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    reference_service = providers.Factory(
        ReferenceService,
        async_db=database,
    )
