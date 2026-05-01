import re
import logging
from uuid import UUID
from messaging.message.service import MessageService
from messaging.signal.service import SignalService

logger = logging.getLogger(__name__)

class MqttHandlers:
    def __init__(self, message_service: MessageService, signal_service: SignalService):
        self.message_service = message_service
        self.signal_service = signal_service

    async def handle(self, topic: str, data: dict):
        # mappa/chat/room/{tenantId}/{roomId}
        room_match = re.match(r"mappa/chat/room/([^/]+)/([^/]+)", topic)
        if room_match:
            tenant_id, room_id = room_match.groups()
            if tenant_id in ('default', 'None', 'undefined'):
                tenant_id = "00000000-0000-0000-0000-000000000000"
            await self._handle_room_chat(tenant_id, room_id, data)
            return

        # mappa/chat/dm/{tenantId}/{userA}/{userB}
        dm_match = re.match(r"mappa/chat/dm/([^/]+)/([^/]+)/([^/]+)", topic)
        if dm_match:
            tenant_id, user_a, user_b = dm_match.groups()
            if tenant_id in ('default', 'None', 'undefined'):
                tenant_id = "00000000-0000-0000-0000-000000000000"
            await self._handle_dm_chat(tenant_id, user_a, user_b, data)
            return

        # mappa/signals/{tenantId}/{layer}/{entityId}
        signal_match = re.match(r"mappa/signals/([^/]+)/([^/]+)/([^/]+)", topic)
        if signal_match:
            tenant_id, layer, entity_id = signal_match.groups()
            if tenant_id in ('default', 'None', 'undefined'):
                tenant_id = "00000000-0000-0000-0000-000000000000"
            await self._handle_signal(tenant_id, layer, entity_id, data)
            return

    async def _handle_room_chat(self, tenant_id: str, room_id: str, data: dict):
        from messaging.message.model import CreateMessage
        
        # Prefer tenant_id from payload if it's a real ID
        t_id = data.get("tenant_id") or tenant_id
        if t_id in ('default', 'None', 'undefined'):
            t_id = "00000000-0000-0000-0000-000000000000"

        file_urls = data.get("file_urls", [])
        if not file_urls and data.get("file_url"):
            file_urls = [data.get("file_url")]

        logger.critical(f"=========================================")
        logger.critical(f"MQTT ROOM PAYLOAD: {data}")
        logger.critical(f"RESOLVED FILE URLS: {file_urls}")
        logger.critical(f"=========================================")

        msg_in = CreateMessage(
            room_id=UUID(room_id),
            message=data.get("message", ""),
            type=data.get("type", "text"),
            file_urls=file_urls
        )
        user_id = data.get("sender_id")
        await self.message_service.create(msg_in, t_id, user_id)

    async def _handle_dm_chat(self, tenant_id: str, user_a: str, user_b: str, data: dict):
        from messaging.message.model import CreateMessage
        logger.info(f"Persisting DM message between {user_a} and {user_b}")
        
        # Prefer tenant_id from payload if it's a real ID
        t_id = data.get("tenant_id") or tenant_id
        if t_id in ('default', 'None', 'undefined'):
            t_id = "00000000-0000-0000-0000-000000000000"

        file_urls = data.get("file_urls", [])
        if not file_urls and data.get("file_url"):
            file_urls = [data.get("file_url")]

        # A is sender, B is receiver
        msg_in = CreateMessage(
            receiver_id=UUID(user_b),
            message=data.get("message", ""),
            type=data.get("type", "text"),
            file_urls=file_urls
        )
        await self.message_service.create(msg_in, t_id, user_a)

    async def _handle_signal(self, tenant_id: str, layer: str, entity_id: str, data: dict):
        logger.debug(f"Signal received for {entity_id} on {layer}")
        await self.signal_service.persist_signal(tenant_id, layer, entity_id, data)
