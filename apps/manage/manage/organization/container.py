from dependency_injector import containers, providers
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService


class OrganizationContainer(containers.DeclarativeContainer):
    """Organization paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    organization_client_service = providers.Dependency()

    organization_service = providers.Factory(
        OrganizationService,
        async_db=database,
        organization_client_service=organization_client_service
    )
