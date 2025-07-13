from dependency_injector import containers, providers
from mapa.spatial.layer.layer_service import LayerService
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService


class LayerContainer(containers.DeclarativeContainer):
    """Layer paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    layer_definition_service = providers.Factory(
        LayerDefinitionService,
        async_db=database
    )
  
    layer_service = providers.Factory(
        LayerService,
        async_db=database,
        layer_definition_service=layer_definition_service
    )
