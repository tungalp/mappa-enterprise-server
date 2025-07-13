from dependency_injector import containers, providers
from mapa.spatial.definition.definition_service import DefinitionService
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService

class DefinitionContainer(containers.DeclarativeContainer):
    """Definition paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
       
    layer_hook_service = providers.Factory(
        LayerHookService,
        async_db=database
    )
   
    layer_definition_service = providers.Factory(
        LayerDefinitionService,
        async_db=database
    )
    
    definition_service = providers.Factory(
        DefinitionService,
        async_db=database,
        layer_definition_service=layer_definition_service,
        layer_hook_service=layer_hook_service
    )
