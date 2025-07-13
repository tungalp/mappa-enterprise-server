from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.user_variable_type.user_variable_type_service import UserVariableTypeService

class UserVariableTypeContainer(containers.DeclarativeContainer):
    """UserVariableType paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    user_variable_type_service = providers.Factory(
        UserVariableTypeService,
        async_db=database
    )
