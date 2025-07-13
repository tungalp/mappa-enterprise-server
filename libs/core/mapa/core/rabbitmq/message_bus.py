import os
from mapa.core.rabbitmq.base_publisher import BasePublisher
from aio_pika.abc import AbstractRobustConnection
import socket
from uuid import UUID
from nanoid import generate
import json
import uuid
from aio_pika import Message
import asyncio
import socket


class MessageBus:
    def __init__(self, exchange_name: str | None = None, connection: AbstractRobustConnection | None = None):
        self.exchange_name = exchange_name or os.getenv("RABBITMQ_EXCHANGE", "mapa-exchange")
        self.publisher = BasePublisher(self.exchange_name, connection=connection)
        self._reply_queue = None
        self._futures = {}
        self._channel = None
        self.x_queue_type = "quorum"
        self._reply_queue_name = f"reply.{socket.gethostname()}.{uuid.uuid4()}"

    async def publish(self, routing_key: str, payload: dict) -> dict | None:
        return await self.publisher.publish(routing_key, payload)
    
    async def _ensure_channel(self):
        if self._channel and not self._channel.is_closed:
            return self._channel

        conn = await self.publisher.connection.get_connection()
        self._channel = await conn.channel()
        self._reply_queue = None  # bağlantı koptuysa reply queue da sıfırlanmalı
        self._listening = False
        return self._channel

    async def _get_reply_queue(self):
        if self._reply_queue:
            return self._reply_queue

        channel = await self._ensure_channel()
        self._reply_queue = await channel.declare_queue(
            self._reply_queue_name,
            durable=False,
            exclusive=True,
            auto_delete=True, 
        )
        if not self._listening:
            asyncio.create_task(self._listen_replies())
            self._listening = True
        return self._reply_queue

    async def _listen_replies(self):
        try:
            async for message in self._reply_queue:
                correlation_id = message.correlation_id
                future = self._futures.pop(correlation_id, None)
                if future:
                    future.set_result(message)
                await message.ack()
        except Exception as ex:
            print(f"[MessageBus] reply listener error: {ex}")
            self._listening = False  # tekrar başlatılabilir olması için

    async def publish_with_response(self, routing_key: str, payload: dict):
        correlation_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        channel = await self._ensure_channel()
        reply_queue = await self._get_reply_queue()

        payload["message_id"] = message_id
        payload["event_id"] = event_id
        
        serialized_payload = json.dumps(payload, default=str)

        message = Message(
            body=serialized_payload.encode(),
            reply_to=reply_queue.name,
            correlation_id=correlation_id
            
        )

        future = asyncio.get_event_loop().create_future()
        self._futures[correlation_id] = future

        await self.publisher.publish(routing_key, message)
        print(f"[MessageBus] Published message with correlation_id={correlation_id}")

        try:
            response_message = await asyncio.wait_for(future, timeout=10)
            print(f"[MessageBus] Received response for correlation_id={correlation_id}")
            return json.loads(response_message.body.decode())
        except asyncio.TimeoutError:
            self._futures.pop(correlation_id, None)
            raise TimeoutError(f"Mesaja ilişkin yanıt '{correlation_id}' süresi içinde alınamadı.")

    async def publish_without_response(self, routing_key: str, payload: dict):
        channel = await self._ensure_channel()
        message_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        
        payload["message_id"] = message_id
        payload["event_id"] = event_id
        
        serialized_payload = json.dumps(payload, default=str)

        message = Message(
            body=serialized_payload.encode(),
        )

        await self.publisher.publish(routing_key, message)