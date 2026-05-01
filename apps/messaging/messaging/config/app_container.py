import os
import pathlib
from dependency_injector import containers, providers
from messaging.room.container import RoomContainer
from messaging.message.container import MessageContainer
from messaging.message.minio_service import MinioService
from messaging.signal.service import SignalService
from messaging.mqtt_processor.processor import MqttProcessor
from messaging.mqtt_processor.handlers import MqttHandlers
from messaging.outbox.container import OutboxContainer
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.message_bus import MessageBus
from messaging.outbox.service_messenger import ServiceMessenger
from mapa.core.data import AsyncDatabase
# We will define these wrappers later or use raw clients
from redis.asyncio import Redis

def get_config_file_names():
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]

class MessagingContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=get_config_file_names(), strict=True)

    db = providers.Singleton(AsyncDatabase, db_url=config.db.url)

    minio_service = providers.Singleton(
        MinioService,
        config=config.minio
    )

    # Redis for Presence & Read Receipts
    redis_client = providers.Singleton(
        Redis,
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password,
        db=config.redis.db,
        decode_responses=True
    )

    # RabbitMQ
    rabbit_connection = providers.Singleton(RabbitConnection, config=config.rabbitmq)
    message_bus = providers.Singleton(
        MessageBus,
        exchange_name=config.rabbitmq.exchange_name,
        connection=rabbit_connection,
    )

    # Outbox
    outbox_package = providers.Container(OutboxContainer, database=db.provided)

    service_messenger = providers.Singleton(
        ServiceMessenger,
        message_bus=message_bus,
        outbox_service=outbox_package.outbox_service,
        async_db=db.provided,
    )

    # Message & Room Packages
    message_package = providers.Container(
        MessageContainer,
        database=db.provided,
        messenger=service_messenger,
        redis=redis_client,
        minio=minio_service
    )

    room_package = providers.Container(
        RoomContainer,
        database=db.provided,
        messenger=service_messenger,
        message_service=message_package.message_service
    )

    signal_service = providers.Singleton(
        SignalService,
        async_db=db.provided
    )

    mqtt_handlers = providers.Singleton(
        MqttHandlers,
        message_service=message_package.message_service,
        signal_service=signal_service
    )

    mqtt_processor = providers.Singleton(
        MqttProcessor,
        config=config.mqtt,
        handlers=mqtt_handlers
    )
