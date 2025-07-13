from dependency_injector import containers, providers
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService


class LayerDefinitionContainer(containers.DeclarativeContainer):
    """LayerDefinition paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    layer_definition_service = providers.Factory(
        LayerDefinitionService,
        async_db=database,
    )
