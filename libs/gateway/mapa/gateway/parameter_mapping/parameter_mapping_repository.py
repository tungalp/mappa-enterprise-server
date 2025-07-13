from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.gateway.parameter_mapping.parameter_mapping_entity import ParameterMappingEntity


class ParameterMappingRepository(BaseRepository[ParameterMappingEntity]):
    """IntegrationParameterMapping Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ParameterMappingEntity)
