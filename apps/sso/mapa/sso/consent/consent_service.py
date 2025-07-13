from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.consent.consent_model import Consent, CreateConsent, UpdateAllConsent, UpdateConsent
from mapa.sso.consent.consent_repository import ConsentRepository


class ConsentService(BaseEntityService[ConsentRepository, Consent, CreateConsent, UpdateConsent, UpdateAllConsent]):
    """Consent Service"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ConsentRepository, Consent)

    async def find_by_keys(self, client_id: UUID, user_id: UUID) -> Consent | None:
        """ClientId ve UserId değerierine göre kaydı bulur"""

        return await self.find_one(QueryArgs(where=[
            Filter(field="client_id", op=FilterOp.EQUAL, value=client_id),
            Filter(field="user_id", op=FilterOp.EQUAL, value=user_id),
        ]))