from dependency_injector import containers, providers
from mapa.spatial.map_layer.map_layer_service import MapLayerService


class MapLayerContainer(containers.DeclarativeContainer):
    """MapLayer paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    map_layer_service = providers.Factory(
        MapLayerService,
        async_db=database,
    )
