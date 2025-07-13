from dependency_injector import containers
from dependency_injector import providers
from mapa.gateway.parameter_mapping.parameter_mapping_service import ParameterMappingService

class ParameterMappingContainer(containers.DeclarativeContainer):
    """ParameterMapping paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    parameter_mapping_service = providers.Factory(
        ParameterMappingService,
        async_db=database
    )
