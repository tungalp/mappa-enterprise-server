from dependency_injector import containers
from dependency_injector import providers
from mapa.application.content_page_template.content_page_template_service import ContentPageTemplateService

class ContentPageTemplateContainer(containers.DeclarativeContainer):
    """ContentPageTemplate paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    content_page_template_service = providers.Factory(
        ContentPageTemplateService,
        async_db=database
    )
