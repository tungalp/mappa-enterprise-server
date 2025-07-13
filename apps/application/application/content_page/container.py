from dependency_injector import containers
from dependency_injector import providers
from mapa.application.content_page.content_page_service import ContentPageService

class ContentPageContainer(containers.DeclarativeContainer):
    """ContentPage paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    content_page_service = providers.Factory(
        ContentPageService,
        async_db=database
    )
