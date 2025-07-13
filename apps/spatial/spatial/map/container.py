from dependency_injector import containers, providers
from mapa.spatial.map.map_service import MapService


class MapContainer(containers.DeclarativeContainer):
    """Map paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    reference_service = providers.Dependency()
    bookmark_service = providers.Dependency()
    map_base_layer_service = providers.Dependency()
    messenger = providers.Dependency()

    map_service = providers.Factory(
        MapService,
        async_db=database,
        reference_service=reference_service,
        bookmark_service=bookmark_service,
        map_base_layer_service=map_base_layer_service,
        messenger= messenger
    )
