import json
from aio_pika import Message, ExchangeType
from mapa.core.rabbitmq.base_connection import RabbitConnection
from aio_pika import Exchange

class BasePublisher:
    def __init__(self, exchange_name: str, connection: RabbitConnection):
        self.exchange_name = exchange_name
        self.connection = connection
        self._channel = None
        self._exchange = None

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

    async def publish(self, routing_key: str, message: Message):
        channel = await self.get_channel()
        exchange = await self.get_exchange()
        await exchange.publish(message, routing_key=routing_key)
