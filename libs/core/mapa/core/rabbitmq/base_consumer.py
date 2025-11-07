import json
from abc import ABC, abstractmethod
from aio_pika import ExchangeType, Message
from mapa.core.data.rabbit_json_encoder import RabbitJsonEncoder
from mapa.core.rabbitmq.base_connection import RabbitConnection
from uuid import UUID
from sqlalchemy.exc import DBAPIError
from redis.asyncio import Redis


class BaseConsumer(ABC):
    def __init__(
        self,
        queue_name: str,
        routing_key: str,
        exchange_name: str,
        connection: RabbitConnection,
        read_redis: Redis,
        write_redis: Redis,
    ):
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self.connection = connection
        self.x_queue_type = "quorum"
        self._consumer_task = None
        self._read_redis = read_redis
        self._write_redis = write_redis
        self._channel = None
        self._exchange = None

    async def start(self):
        await self.consume()
        # reconnect olduğunda consume tekrar çalışsın
        self.connection.add_reconnect_callback(self.on_reconnect)

    async def get_channel(self):
        if self._channel and not self._channel.is_closed:
            return self._channel
        conn = await self.connection.get_connection()
        self._channel = await conn.channel()
        return self._channel

    async def get_exchange(self):
        if self._exchange:
            return self._exchange
        channel = await self.get_channel()
        self._exchange = await channel.declare_exchange(
            self.exchange_name, ExchangeType.DIRECT, durable=True
        )
        return self._exchange

    async def on_reconnect(self, conn):
        print(f"[Reconnect] Reinitializing consumer for: {self.queue_name}")
        await self.consume()

    async def consume(self):
        conn = await self.connection.get_connection()
        channel = await self.get_channel()
        exchange = await self.get_exchange()
        queue = await channel.declare_queue(
            self.queue_name, durable=True, arguments={"x-queue-type": self.x_queue_type}
        )
        await queue.bind(exchange, routing_key=self.routing_key)

        async def message_loop():
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        payload = json.loads(message.body.decode())

                        message_id = payload.get("message_id")
                        event_id = payload.get("event_id")
                        if await self.is_duplicate(message_id, event_id):
                            await message.ack()
                            continue

                        response = await self.process_message(payload)

                        if response is not None:
                            reply_to = message.reply_to
                            if reply_to:
                                await self.send_response(reply_to, response, message.correlation_id)  # type: ignore

                        await message.ack()

                    except DBAPIError as db_error:
                        print(f"Database error: {db_error}")
                        response = {
                            "error": str(db_error),
                            "message": "Database operation failed.",
                        }
                        reply_to = message.reply_to
                        if reply_to:
                            await self.send_response(reply_to, response, message.correlation_id)  # type: ignore
                        await message.ack()

                    except Exception as e:
                        print(f"Error processing message: {e}")
                        await message.nack(requeue=True)

        # Task olarak başlat
        if self._consumer_task is not None:
            self._consumer_task.cancel()

        import asyncio

        self._consumer_task = asyncio.create_task(message_loop())

    async def send_response(self, reply_to: str, response: dict, correlation_id: str):
        try:
            conn = await self.connection.get_connection()
            channel = await self.get_channel()

            serialized_payload = json.dumps(response, cls=RabbitJsonEncoder)

            message = Message(
                body=serialized_payload.encode(),
                correlation_id=correlation_id,
            )
            await channel.default_exchange.publish(message, routing_key=reply_to)
            print(f"[BaseConsumer] Response sent: correlation_id={correlation_id}, reply_to={reply_to}")
        except Exception as ex:
            print(f"[BaseConsumer] Error sending response: correlation_id={correlation_id}, reply_to={reply_to}, error={ex}")
            raise

    async def is_duplicate(self, message_id: str, event_id: str) -> bool:
        redis_key = f"idempotent:{self.queue_name}:{message_id}:{event_id}"
        already_processed = await self._read_redis.get(redis_key)
        if already_processed:
            return True
        await self._write_redis.set(redis_key, "1", ex=12 * 3600)
        return False

    @abstractmethod
    async def process_message(self, payload: dict):
        pass
