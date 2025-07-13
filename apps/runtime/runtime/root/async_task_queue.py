"""Module for async task queue"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Tuple
from mapa.service.function import FunctionRequest

class AsyncTaskQueue:
    """Class for async task queue
    """
    
    def __init__(self) -> None:
        self.tasks_queue_map: Dict[str,  asyncio.Queue] = {}
        self.response_map: Dict[str, Tuple[asyncio.Future, datetime]] = {}
        self.lock = asyncio.Lock()  # Lock for thread-safe operations
        self.loop = asyncio.get_event_loop()
        
        
    async def enqueue_task(self, runtime_id: str, request: FunctionRequest) -> asyncio.Future:
        """Enqueue a task and return a Future object for the caller to await."""

        # Her container için ayrı bir liste tutulur.
        task_queue = await self._create_or_get_task_queue(runtime_id)
        
        # Add the task to the queue.
        await task_queue.put(request)
        
        # Generate a unique ID for this task.
        task_id = request.id

        # Create a Future object for this task's response.
        response_future = asyncio.Future()
        async with self.lock:
            expiration_time = datetime.now() + timedelta(seconds=request.timeout)
            self.response_map[task_id] = (response_future, expiration_time)

        # Schedule the timeout check without directly sleeping
        self.loop.call_later(
            request.timeout,
            lambda: asyncio.create_task(self.__check_timeout(request.id))
        )

        # return the Future object for the caller to await.
        return response_future
    
    async def dequeue_task(self, runtime_id: str):
        """Dequeue a task from the queue and return it."""

        task_queue = await self._create_or_get_task_queue(runtime_id)
        
        # Retrieve the next task from the queue.
        task_data = await task_queue.get()

        return task_data
    
    async def _create_or_get_task_queue(self, runtime_id: str) -> asyncio.Queue:
        task_queue = self.tasks_queue_map.get(runtime_id)
        if not task_queue:
            task_queue = asyncio.Queue()
            async with self.lock:
                self.tasks_queue_map[runtime_id] = task_queue
        return task_queue
    
    async def __check_timeout(self, identifier):
        """Check if the future has expired and handle it."""
        async with self.lock:
            future_info = self.response_map.pop(identifier, None)
            if future_info:
                future, expiration_time = future_info
                if not future.done() and datetime.now() >= expiration_time:
                    future.set_exception(TimeoutError("Future timed out"))
