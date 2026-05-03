from dependency_injector import containers, providers
from mapa.spatial.file_store.file_store_service import FileStoreService


class FileStoreContainer(containers.DeclarativeContainer):
    """FileStore paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    minio_service = providers.Dependency()

    file_store_service = providers.Factory(
        FileStoreService,
        async_db=database,
        minio_service=minio_service
    )

