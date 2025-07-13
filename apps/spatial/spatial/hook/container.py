from dependency_injector import containers, providers
from mapa.spatial.hook.hook_service import HookService


class HookContainer(containers.DeclarativeContainer):
    """Hook paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    hook_service = providers.Factory(
        HookService,
        async_db=database,
    )
