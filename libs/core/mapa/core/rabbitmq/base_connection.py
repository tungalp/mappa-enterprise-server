from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from typing import Optional, Callable, Awaitable, List


class RabbitConnection:
    def __init__(self, config: dict):
        self.config = config
        self._connection: Optional[AbstractRobustConnection] = None
        self._reconnect_callbacks: List[Callable[[AbstractRobustConnection], Awaitable[None]]] = []

    def add_reconnect_callback(self, callback: Callable[[AbstractRobustConnection], Awaitable[None]]):
        self._reconnect_callbacks.append(callback)

    async def get_connection(self) -> AbstractRobustConnection:
        if self._connection and not self._connection.is_closed:
            return self._connection

        self._connection = await connect_robust(
            host=self.config.get("host", "localhost"),
            port=int(self.config.get("port", 5672)),
            login=self.config.get("username", "guest"),
            password=self.config.get("password", "guest"),
            virtualhost=self.config.get("virtual_host", "/"),
        )

        # Reconnect durumunda tetiklenecek callback'leri bağla
        for callback in self._reconnect_callbacks:
            self._connection.reconnect_callbacks.add(callback) # type: ignore

        return self._connection