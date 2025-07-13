from dependency_injector import containers
from dependency_injector import providers
from .async_task_queue import AsyncTaskQueue

class RootContainer(containers.DeclarativeContainer):
    """Root paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()
    
    task_queue = providers.Singleton(
        AsyncTaskQueue
    )