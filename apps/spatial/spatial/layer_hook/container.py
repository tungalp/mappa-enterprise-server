from dependency_injector import containers, providers
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService


class LayerHookContainer(containers.DeclarativeContainer):
    """LayerHook paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    layer_hook_service = providers.Factory(
        LayerHookService,
        async_db=database,
    )
