from dependency_injector import containers, providers
from mapa.spatial.base_layer.base_layer_service import BaseLayerService


class BaseLayerContainer(containers.DeclarativeContainer):
    """BaseLayer paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    base_layer_service = providers.Factory(
        BaseLayerService,
        async_db=database,
    )
