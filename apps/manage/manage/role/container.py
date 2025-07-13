from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.role.role_service import RoleService

class RoleContainer(containers.DeclarativeContainer):
    """Rol paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    role_service = providers.Factory(
        RoleService,
        async_db=database
    )
