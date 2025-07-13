from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.role_user.role_user_service import RoleUserService

class RoleUserContainer(containers.DeclarativeContainer):
    """RoleUser paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    role_user_service = providers.Factory(
        RoleUserService,
        async_db=database
    )
