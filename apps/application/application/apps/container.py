from dependency_injector import containers
from dependency_injector import providers
from mapa.application.app.app_service import AppService


class AppContainer(containers.DeclarativeContainer):
    """App paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    content_page_service = providers.Dependency()
    messenger = providers.Dependency()
    
    app_service = providers.Factory(
        AppService,
        async_db=database,        
        content_page_service=content_page_service,
        messenger= messenger
    )
