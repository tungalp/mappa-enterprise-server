import os
import pathlib
from dependency_injector import containers, providers
from mapa.core.data import AsyncDatabase
from desktop_mobile.services.storage import MinioService
from desktop_mobile.models.repositories import ApiKeyPermissionRepository
from desktop_mobile.services.business_services import (
    CollectionService,
    MapService,
    LayerService,
    ApiKeyService,
    ApiKeyPermissionService
)

def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]

class AppContainer(containers.DeclarativeContainer):
    """desktop_mobile microservice DI container layout."""
    
    # Configuration
    config = providers.Configuration(yaml_files=get_config_file_names(), strict=True)
    
    # Async DB Engine
    db = providers.Singleton(AsyncDatabase, db_url=config.db.url)
    
    # MinIO Storage Service
    minio_service = providers.Singleton(
        MinioService,
        config=config.minio
    )
    
    # Api Key Permissions Repository
    permission_repo = providers.Singleton(
        ApiKeyPermissionRepository,
        async_db=db.provided
    )
    
    # Core Entity Services
    collection_service = providers.Singleton(
        CollectionService,
        async_db=db.provided
    )
    
    map_service = providers.Singleton(
        MapService,
        async_db=db.provided,
        minio_service=minio_service
    )
    layer_service = providers.Singleton(
        LayerService,
        async_db=db.provided,
        minio_service=minio_service
    )
    
    api_key_service = providers.Singleton(
        ApiKeyService,
        async_db=db.provided,
        permission_repo=permission_repo
    )
    
    api_key_permission_service = providers.Singleton(
        ApiKeyPermissionService,
        async_db=db.provided
    )

