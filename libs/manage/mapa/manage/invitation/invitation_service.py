from typing import List
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.invitation.invitation_model import CreateInvitation, Invitation, UpdateAllInvitation, UpdateInvitation
from mapa.manage.invitation.invitation_repository import InvitationRepository
from uuid import UUID
from datetime import datetime, timedelta
from mapa.manage.user.user_model import User

class InvitationService(BaseEntityService[InvitationRepository, Invitation, CreateInvitation, UpdateInvitation, UpdateAllInvitation]):
    """InvitationService""" 

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, InvitationRepository, Invitation)

    async def create(self, invitation: CreateInvitation, tenant_id: str | None = None) -> Invitation:
        # Not : Davetiye nin total süresi profil kısmından ayarlanabilir TODO 16.02.2024
        invitation.expired_at = datetime.now() + timedelta(days=7)
        return await super().create(invitation, tenant_id)
    
    async def create_all(self, invitations: List[CreateInvitation], tenant_id: str | None = None) -> List[Invitation]:
        # Not : Davetiye nin total süresi profil kısmından ayarlanabilir TODO 16.02.2024
        for invitation in invitations:
            invitation.expired_at = datetime.now() + timedelta(days=7)
            
        created_organization_clients = await super().create_all(invitations, tenant_id)
        return created_organization_clients
    
    async def delete_user_info(self, users: List[User], tenant_id: str | None = None) -> int:
        # Not : User silindiği zaman kendisine ait davetiyelerde siliniyor.
        deleted_count = 0
        for user in users:
            query_args = QueryArgs(where=[
                Filter(field="email",
                       op=FilterOp.EQUAL, value=user.email),
            ], limit=0, offset=0)
            deleted_count = await super().delete_all(query_args, tenant_id)
            
        return deleted_count