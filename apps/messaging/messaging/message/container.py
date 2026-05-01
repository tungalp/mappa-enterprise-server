from dependency_injector import containers, providers
from messaging.message.service import MessageService

class MessageContainer(containers.DeclarativeContainer):
    database = providers.Dependency()
    messenger = providers.Dependency()
    redis = providers.Dependency()

    minio = providers.Dependency()

    message_service = providers.Singleton(
        MessageService,
        async_db=database,
        redis=redis,
        minio_service=minio
    )
