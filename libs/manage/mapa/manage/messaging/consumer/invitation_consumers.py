from typing import List
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.invitation.invitation_model import UpdateInvitation
from mapa.manage.invitation.invitation_service import InvitationService
from redis.asyncio import Redis




class InvitationUpdateConsumer(BaseConsumer):
    def __init__(self, invitation_service: InvitationService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("invitation.update", "invitation.update", "mapa-exchange", connection, rredis, wredis)
        self.service = invitation_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        id = payload["id"]
        invitation = UpdateInvitation(**data)
        tenant_id = payload.get("tenant_id")
        updated = await self.service.update(id, invitation, tenant_id)
        return {"id": id}


class InvitationGetConsumer(BaseConsumer):
    def __init__(self, invitation_service: InvitationService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("invitation.get", "invitation.get", "mapa-exchange", connection, rredis, wredis)
        self.service = invitation_service

    async def process_message(self, payload: dict) -> dict:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        fields = payload.get("fields", [])
        result = await self.service.get(id, tenant_id, fields)
        if result is None:
            return {}
        return result.model_dump()
