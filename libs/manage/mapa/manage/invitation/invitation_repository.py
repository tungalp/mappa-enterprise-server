from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.invitation.invitation_entity import InvitationEntity


class InvitationRepository(BaseRepository[InvitationEntity]):
    """Invitation Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, InvitationEntity)
