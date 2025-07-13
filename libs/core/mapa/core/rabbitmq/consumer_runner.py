import asyncio
from typing import List

class ConsumerRunner:
    def __init__(self, consumers: List):
        self.consumers = consumers

    async def start(self):
        tasks = []
        for consumer in self.consumers:
            tasks.append(asyncio.create_task(consumer.start()))
        await asyncio.gather(*tasks)