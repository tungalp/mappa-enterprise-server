from dependency_injector import containers, providers
from mapa.spatial.layer.layer_service import LayerService
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.map_layer.map_layer_service import MapLayerService


class LayerContainer(containers.DeclarativeContainer):
    """Layer paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    layer_definition_service = providers.Factory(
        LayerDefinitionService,
        async_db=database
    )
    
    map_layer_service = providers.Factory(
        MapLayerService,
        async_db=database
    )
  
    layer_service = providers.Factory(
        LayerService,
        async_db=database,
        layer_definition_service=layer_definition_service,
        map_layer_service=map_layer_service
    )
