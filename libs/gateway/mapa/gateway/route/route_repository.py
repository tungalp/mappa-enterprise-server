from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.route.route_entity import RouteEntity


class RouteRepository(BaseRepository[RouteEntity]):
    """Route Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RouteEntity)
