import os
import pathlib
from dependency_injector import containers
from dependency_injector import providers
from mapa.core.data import AsyncDatabase
from runtime.root.container import RootContainer


def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [
        config_path + "/config.yml",
        config_file_name
    ]


class AppContainer(containers.DeclarativeContainer):
    """Genel uygulama servis ve DI konteyner yapısı.
    Uygulamadaki veritabanı bağlantısı, alt konteynerlar ve bunların
    birbirlerine olan bağımlılıkları burada tanımlanır.
    """

    # Genel uygulama konfigürasyon bilgileri
    config = providers.Configuration(
        yaml_files=get_config_file_names(), strict=True
    )

    # Veritabanı
    db = providers.Singleton(AsyncDatabase, db_url=config.db.url)
    
    
    # Root package
    root_package = providers.Container(
        RootContainer,
        database=db.provided
    )
