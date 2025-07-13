from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.gateway.context_var.context_var_model import ConvextVar, CreateConvextVar, UpdateAllConvextVar, UpdateConvextVar
from mapa.gateway.context_var.context_var_repository import ContextVarRepository

class ContextVarService(BaseEntityService[ContextVarRepository, ConvextVar, CreateConvextVar, UpdateConvextVar, UpdateAllConvextVar]):
    """Integration Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ContextVarRepository, ConvextVar)
