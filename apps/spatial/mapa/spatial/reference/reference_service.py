from typing import Any, Dict, List

from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.reference.reference_model import (CreateReference, Reference,
                                                   UpdateAllReference,
                                                   UpdateReference)
from mapa.spatial.reference.reference_repository import ReferenceRepository


class ReferenceService(BaseEntityService[ReferenceRepository, Reference, CreateReference, UpdateReference, UpdateAllReference]):
    """Reference Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ReferenceRepository, Reference)
