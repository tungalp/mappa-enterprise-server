from dependency_injector import containers, providers
from messaging.outbox.service import OutboxService

class OutboxContainer(containers.DeclarativeContainer):
    database = providers.Dependency()
    
    outbox_service = providers.Factory(
        OutboxService,
        async_db=database
    )
