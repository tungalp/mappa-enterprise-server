
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.layer_hook.layer_hook_model import (CreateLayerHook,
                                                     LayerHook,
                                                     UpdateAllLayerHook,
                                                     UpdateLayerHook)
from mapa.spatial.layer_hook.layer_hook_repository import LayerHookRepository


class LayerHookService(BaseEntityService[LayerHookRepository, LayerHook, CreateLayerHook, UpdateLayerHook, UpdateAllLayerHook]):
    """LayerHook Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, LayerHookRepository, LayerHook)
