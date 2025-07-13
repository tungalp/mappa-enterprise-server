from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.gateway.parameter_mapping.parameter_mapping_model import CreateParameterMapping, UpdateAllParameterMapping, UpdateParameterMapping, ParameterMapping
from mapa.gateway.parameter_mapping.parameter_mapping_repository import ParameterMappingRepository

class ParameterMappingService(BaseEntityService[ParameterMappingRepository, ParameterMapping, CreateParameterMapping, UpdateParameterMapping, UpdateAllParameterMapping]):
    """IntegrationParameterMapping Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ParameterMappingRepository, ParameterMapping)
    