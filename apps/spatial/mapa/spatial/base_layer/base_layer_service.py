from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.base_layer.base_layer_model import (BaseLayer,
                                                     CreateBaseLayer,
                                                     UpdateAllBaseLayer,
                                                     UpdateBaseLayer)
from mapa.spatial.base_layer.base_layer_repository import BaseLayerRepository


class BaseLayerService(BaseEntityService[BaseLayerRepository, BaseLayer, CreateBaseLayer, UpdateBaseLayer, UpdateAllBaseLayer]):
    """BaseLayer Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, BaseLayerRepository, BaseLayer)
