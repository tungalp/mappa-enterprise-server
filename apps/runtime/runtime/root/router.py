from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.service.function import FunctionRequest
from mapa.service.response import ServiceResponse
from runtime.config.app_container import AppContainer
from runtime.root.async_task_queue import AsyncTaskQueue

router = APIRouter()

@router.post("/task/{runtime_id}", response_model=ServiceResponse)
@inject
async def post_task(
    runtime_id: str,
    request: Request,
    function_request: FunctionRequest = Body(...),
    task_queue: AsyncTaskQueue = Depends(
        Provide[AppContainer.root_package.task_queue])):
    """TaskId ye bağlı olan görevi tamamlar"""
    
    future = await task_queue.enqueue_task(runtime_id, function_request)

    # Dönüş değeri beklenir
    response = await future

    # Dönüş değeri gönderilir.
    return response


@router.get("/request/{runtime_id}", response_model=FunctionRequest)
@inject
async def get_request(
    request: Request,
    runtime_id: str,
    task_queue: AsyncTaskQueue = Depends(
        Provide[AppContainer.root_package.task_queue])):
    """Kuyruktan bir işi alır ve geri döner
    """
    service_request = await task_queue.dequeue_task(runtime_id)
    
    if not service_request:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return service_request

@router.post("/response/{task_id}")
@inject
async def post_response(
    task_id: str,
    request: Request,
    service_response: ServiceResponse = Body(...),
    task_queue: AsyncTaskQueue = Depends(
        Provide[AppContainer.root_package.task_queue])):
    """TaskId ye bağlı olan görevi tamamlar"""
    
    if task_id not in task_queue.response_map:
        raise HTTPException(status_code=404, detail="Task not found")
    
    future = task_queue.response_map.pop(task_id, None)
    if future:
        future[0].set_result(service_response)
    else:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Task completed"})