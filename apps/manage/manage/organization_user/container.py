from dependency_injector import containers, providers
from mapa.manage.organization_user.organization_user_service import OrganizationUserService


class OrganizationUserContainer(containers.DeclarativeContainer):
    """OrganizationUser paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    organization_user_service = providers.Factory(
        OrganizationUserService,
        async_db=database,
    )
