from dependency_injector import containers
from dependency_injector import providers

from mapa.application.outbox.outbox_service import OutboxService

class OutboxContainer(containers.DeclarativeContainer):
    """Outbox paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    outbox_service = providers.Factory(
        OutboxService,
        async_db=database
    )
