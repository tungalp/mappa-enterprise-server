from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.namespace.namespace_model import (CreateNamespace, Namespace,
                                                   UpdateAllNamespace,
                                                   UpdateNamespace)
from mapa.spatial.namespace.namespace_repository import NamespaceRepository


class NamespaceService(BaseEntityService[NamespaceRepository, Namespace, CreateNamespace, UpdateNamespace, UpdateAllNamespace]):
    """Namespace Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, NamespaceRepository, Namespace)
