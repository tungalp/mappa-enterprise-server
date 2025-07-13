from dependency_injector import containers, providers
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService


class OrganizationTypeContainer(containers.DeclarativeContainer):
    """OrganizationType paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    organization_type_service = providers.Factory(
        OrganizationTypeService,
        async_db=database,
    )
