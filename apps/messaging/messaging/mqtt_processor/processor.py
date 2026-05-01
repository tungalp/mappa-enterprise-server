import asyncio
import json
import logging
from typing import Any
import aiomqtt
from messaging.mqtt_processor.handlers import MqttHandlers

logger = logging.getLogger(__name__)

class MqttProcessor:
    def __init__(self, config: Any, handlers: MqttHandlers):
        self.config = config
        self.handlers = handlers
        self._task = None

    async def start(self):
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        reconnect_interval = 5
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=self.config["host"],
                    port=self.config["port"],
                    username=self.config["username"],
                    password=self.config["password"],
                    identifier="mappa-messaging-backend"
                ) as client:
                    logger.info("Connected to MQTT broker")
                    await client.subscribe("mappa/#")
                    
                    async for message in client.messages:
                        topic = str(message.topic)
                        payload = message.payload.decode()
                        
                        # Process in background task to avoid blocking the loop
                        asyncio.create_task(self._handle_safe(topic, payload))
                        
            except aiomqtt.MqttError as e:
                logger.error(f"MQTT error: {e}. Reconnecting in {reconnect_interval}s...")
                await asyncio.sleep(reconnect_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Unexpected MQTT processor error: {e}")
                await asyncio.sleep(reconnect_interval)

    async def _handle_safe(self, topic: str, payload: str):
        try:
            data = json.loads(payload)
            await self.handlers.handle(topic, data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload on topic {topic}")
        except Exception as e:
            logger.exception(f"Error handling MQTT message on {topic}: {e}")
