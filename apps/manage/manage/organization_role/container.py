from dependency_injector import containers, providers
from mapa.manage.organization_role.organization_role_service import OrganizationRoleService


class OrganizationRoleContainer(containers.DeclarativeContainer):
    """OrganizationRole paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    organization_role_service = providers.Factory(
        OrganizationRoleService,
        async_db=database,
    )
