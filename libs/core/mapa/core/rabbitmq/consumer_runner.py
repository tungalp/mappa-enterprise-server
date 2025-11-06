import asyncio
from typing import List

class ConsumerRunner:
    def __init__(self, consumers: List):
        self.consumers = consumers
        self.tasks = []

    async def start(self):
        # Start consumers as background tasks without blocking
        for consumer in self.consumers:
            task = asyncio.create_task(consumer.start())
            self.tasks.append(task)

        # Give consumers a moment to initialize and report any immediate errors
        if self.tasks:
            done, pending = await asyncio.wait(self.tasks, timeout=10, return_when=asyncio.FIRST_EXCEPTION)
            # Check if any tasks failed with exceptions (both completed and still pending)
            for task in done:
                if task.exception():
                    raise task.exception()

            # Check pending tasks for any that might have hung/failed
            failed_pending = []
            for task in pending:
                if task.done() and task.exception():
                    failed_pending.append(task.exception())

            if failed_pending:
                raise failed_pending[0]

            # Log which consumers are still initializing
            if pending:
                print(f"[ConsumerRunner] {len(pending)} consumers still initializing after 10 seconds")

        print(f"[ConsumerRunner] Started {len(self.tasks)} consumers in background")

    async def stop(self):
        # Cancel all consumer tasks on shutdown
        for task in self.tasks:
            if not task.done():
                task.cancel()
        # Wait for all tasks to complete cancellation
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)