from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.profile_adaptor.profile_adaptor_service import ProfileAdaptorService

class ProfileAdaptorContainer(containers.DeclarativeContainer):
    """ProfileAdaptor paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    profile_adaptor_service = providers.Factory(
        ProfileAdaptorService,
        async_db=database
    )
