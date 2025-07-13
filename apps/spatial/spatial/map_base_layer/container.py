from dependency_injector import containers, providers
from mapa.spatial.map_base_layer.map_base_layer_service import \
    MapBaseLayerService


class MapBaseLayerContainer(containers.DeclarativeContainer):
    """MapBaseLayer paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    map_base_layer_service = providers.Factory(
        MapBaseLayerService,
        async_db=database,
    )
