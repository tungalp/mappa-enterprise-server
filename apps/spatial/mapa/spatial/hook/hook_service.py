from typing import Any, Dict, List

from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.hook.hook_model import (CreateHook, Hook, UpdateAllHook,
                                         UpdateHook)
from mapa.spatial.hook.hook_repository import HookRepository


class HookService(BaseEntityService[HookRepository, Hook, CreateHook, UpdateHook, UpdateAllHook]):
    """Hook Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, HookRepository, Hook)
