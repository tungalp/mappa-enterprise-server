from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.integration.integration_entity import IntegrationEntity


class IntegrationRepository(BaseRepository[IntegrationEntity]):
    """Integration Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, IntegrationEntity)
