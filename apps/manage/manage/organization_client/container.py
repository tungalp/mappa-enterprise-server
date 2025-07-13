from dependency_injector import containers, providers
from mapa.manage.organization_client.organization_client_service import OrganizationClientService


class OrganizationClientContainer(containers.DeclarativeContainer):
    """OrganizationClient paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    organization_client_service = providers.Factory(
        OrganizationClientService,
        async_db=database,
    )
