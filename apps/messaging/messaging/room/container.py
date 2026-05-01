from dependency_injector import containers, providers
from messaging.room.service import RoomService

class RoomContainer(containers.DeclarativeContainer):
    database = providers.Dependency()
    messenger = providers.Dependency()

    message_service = providers.Dependency()

    room_service = providers.Singleton(
        RoomService,
        async_db=database,
        message_service=message_service
    )
