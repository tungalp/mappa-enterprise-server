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
import logging

logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(self, exchange_name: str | None = None, connection: AbstractRobustConnection | None = None):
        self.exchange_name = exchange_name or os.getenv("RABBITMQ_EXCHANGE", "mapa-exchange")
        self.publisher = BasePublisher(self.exchange_name, connection=connection)
        self._reply_queue = None
        self._futures = {}
        self._channel = None
        self.x_queue_type = "quorum"
        self._reply_queue_name = f"reply.{socket.gethostname()}.{uuid.uuid4()}"
        self._listener_task = None
        self._listener_lock = asyncio.Lock()

    async def publish(self, routing_key: str, payload: dict) -> dict | None:
        return await self.publisher.publish(routing_key, payload)
    
    async def _ensure_channel(self):
        if self._channel and not self._channel.is_closed:
            return self._channel

        conn = await self.publisher.connection.get_connection()
        self._channel = await conn.channel()
        self._reply_queue = None  # bağlantı koptuysa reply queue da sıfırlanmalı
        # Cancel old listener task if it exists
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
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
        # Start listener if not already running
        async with self._listener_lock:
            if not self._listener_task or self._listener_task.done():
                self._listener_task = asyncio.create_task(self._listen_replies())
                logger.info(f"[MessageBus] Started reply listener for queue: {self._reply_queue_name}")
        return self._reply_queue

    async def _listen_replies(self):
        try:
            logger.info(f"[MessageBus] Reply listener started for queue: {self._reply_queue_name}")
            async for message in self._reply_queue:
                correlation_id = message.correlation_id
                future = self._futures.pop(correlation_id, None)
                if future and not future.done():
                    future.set_result(message)
                    logger.debug(f"[MessageBus] Resolved future for correlation_id={correlation_id}")
                await message.ack()
        except asyncio.CancelledError:
            logger.info(f"[MessageBus] Reply listener cancelled for queue: {self._reply_queue_name}")
            raise
        except Exception as ex:
            logger.error(f"[MessageBus] Reply listener error: {ex}", exc_info=True)
            # Resolve any pending futures with error
            for correlation_id, future in list(self._futures.items()):
                if not future.done():
                    future.set_exception(ex)
                    self._futures.pop(correlation_id, None)

    async def publish_with_response(self, routing_key: str, payload: dict, timeout: int):
        correlation_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        await self._ensure_channel()
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

        try:
            await self.publisher.publish(routing_key, message)
            logger.info(f"[MessageBus] Published message with correlation_id={correlation_id}, routing_key={routing_key}")
            timeout = int(os.getenv("RABBIT_RPC_TIMEOUT", "60"))
            response_message = await asyncio.wait_for(future, timeout=timeout)
            logger.info(f"[MessageBus] Received response for correlation_id={correlation_id}")
            return json.loads(response_message.body.decode())
        except asyncio.TimeoutError:
            self._futures.pop(correlation_id, None)
            logger.error(f"[MessageBus] Timeout waiting for response: correlation_id={correlation_id}, routing_key={routing_key}, timeout={timeout}s, pending_futures={len(self._futures)}")
            raise TimeoutError(f"Mesaja ilişkin yanıt '{correlation_id}' süresi içinde alınamadı.")
        except Exception as ex:
            self._futures.pop(correlation_id, None)
            logger.error(f"[MessageBus] Error in publish_with_response: correlation_id={correlation_id}, routing_key={routing_key}, error={ex}", exc_info=True)
            raise

    async def publish_without_response(self, routing_key: str, payload: dict):
        await self._ensure_channel()
        message_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())

        payload["message_id"] = message_id
        payload["event_id"] = event_id

        serialized_payload = json.dumps(payload, default=str)

        message = Message(
            body=serialized_payload.encode(),
        )

        try:
            await self.publisher.publish(routing_key, message)
            logger.info(f"[MessageBus] Published message without response: routing_key={routing_key}, message_id={message_id}")
        except Exception as ex:
            logger.error(f"[MessageBus] Error publishing message: routing_key={routing_key}, message_id={message_id}, error={ex}", exc_info=True)
            raise