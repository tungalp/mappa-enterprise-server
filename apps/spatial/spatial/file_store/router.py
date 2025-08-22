from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.file_store.file_store_model import CreateFileStore, UpdateFileStore
from mapa.spatial.file_store.file_store_service import FileStoreService
from mapa.spatial.constant import ApiScopeType
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{file_store_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_FILESTORE])
@inject
async def find(
    request: Request,
    file_store_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    file_store = await file_store_service.get(file_store_id, tenant_id, field_list)
    if not file_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return file_store



@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_FILESTORE])
@inject
async def create(
    request: Request,
    items: List[CreateFileStore] = Body(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service])
):
    tenant_id = request.user.tenant_id
    user_id = request.user.sub
    file_stores = await file_store_service.create_all(items, tenant_id, user_id)
    result = ActionResult(success=True, items=file_stores)
    return result


@router.put("/{file_store_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_FILESTORE])
@inject
async def update(
    request: Request,
    file_store_id: str,
    item: UpdateFileStore = Body(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service])
):
    tenant_id = request.user.tenant_id
    user_id = request.user.sub
    file_stores = await file_store_service.update(file_store_id, item, tenant_id, user_id)
    if not file_stores:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[file_stores], affected=1)
    return result


@router.delete("/{file_store_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_FILESTORE])
@inject
async def delete(
    request: Request,
    file_store_id: str,
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service])
):
    tenant_id = request.user.tenant_id
    is_success = await file_store_service.delete(file_store_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())

@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_FILESTORE])
@inject
async def delete_by_ids(
    request: Request,
    file_store_ids: List[str],
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await file_store_service.delete_by_ids(file_store_ids, tenant_id)
    is_success = True if deleted_count == len(file_store_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
