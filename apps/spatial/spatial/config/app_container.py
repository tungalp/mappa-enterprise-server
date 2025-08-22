import os
import pathlib

from dependency_injector import containers, providers
from mapa.core.data import AsyncDatabase
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.message_bus import MessageBus
from mapa.spatial.messaging.producer.service_messenger import ServiceMessenger
from spatial.base_layer.container import BaseLayerContainer
from spatial.bookmark.container import BookmarkContainer
from spatial.connection.container import ConnectionContainer
from spatial.file_store.container import FileStoreContainer
from spatial.definition.container import DefinitionContainer
from spatial.hook.container import HookContainer
from spatial.layer.container import LayerContainer
from spatial.layer_definition.container import LayerDefinitionContainer
from spatial.layer_hook.container import LayerHookContainer
from spatial.map.container import MapContainer
from spatial.map_base_layer.container import MapBaseLayerContainer
from spatial.map_layer.container import MapLayerContainer
from spatial.namespace.container import NamespaceContainer
from spatial.outbox.container import OutboxContainer
from spatial.reference.container import ReferenceContainer


def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]


class AppContainer(containers.DeclarativeContainer):
    """Genel uygulama servis ve DI konteyner yapısı.
    Uygulamadaki veritabanı bağlantısı, alt konteynerlar ve bunların
    birbirlerine olan bağımlılıkları burada tanımlanır.
    """

    # Genel uygulama konfigürasyon bilgileri
    config = providers.Configuration(yaml_files=get_config_file_names(), strict=True)

    # Veritabanı
    db = providers.Singleton(AsyncDatabase, db_url=config.db.url)

    outbox_package = providers.Container(OutboxContainer, database=db.provided)

    rabbit_connection = providers.Singleton(RabbitConnection, config=config.rabbitmq)

    message_bus = providers.Singleton(
        MessageBus,
        exchange_name=config.rabbitmq.exchange_name,
        connection=rabbit_connection,
    )

    service_messenger = providers.Singleton(
        ServiceMessenger,
        message_bus=message_bus,
        outbox_service=outbox_package.outbox_service,
        async_db=db.provided,
    )

    namespace_package = providers.Container(NamespaceContainer, database=db.provided)

    connection_package = providers.Container(ConnectionContainer, database=db.provided)
    
    file_store_package = providers.Container(FileStoreContainer, database=db.provided)

    layer_definition_package = providers.Container(
        LayerDefinitionContainer, database=db.provided
    )

    layer_package = providers.Container(
        LayerContainer,
        database=db.provided,
        layer_definition_service=layer_definition_package.layer_definition_service,
    )

    definition_package = providers.Container(
        DefinitionContainer,
        database=db.provided,
        layer_definition_service=layer_definition_package.layer_definition_service,
    )

    map_layer_package = providers.Container(MapLayerContainer, database=db.provided)

    reference_package = providers.Container(ReferenceContainer, database=db.provided)

    bookmark_package = providers.Container(BookmarkContainer, database=db.provided)

    base_layer_package = providers.Container(BaseLayerContainer, database=db.provided)

    map_base_layer_package = providers.Container(
        MapBaseLayerContainer, database=db.provided
    )

    hook_package = providers.Container(HookContainer, database=db.provided)

    layer_hook_package = providers.Container(LayerHookContainer, database=db.provided)

    map_package = providers.Container(
        MapContainer,
        database=db.provided,
        reference_service=reference_package.reference_service,
        bookmark_service=bookmark_package.bookmark_service,
        map_base_layer_service=map_base_layer_package.map_base_layer_service,
        messenger=service_messenger,
    )
