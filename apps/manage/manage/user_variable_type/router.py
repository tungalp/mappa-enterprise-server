from typing import Any, Dict, List
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult,PagingResult
from mapa.manage.user_variable_type.user_variable_type_model import CreateUserVariableType, UserVariableType, UpdateAllUserVariableType, UpdateUserVariableType
from manage.config.app_container import AppContainer
from mapa.manage.user_variable_type.user_variable_type_service import UserVariableTypeService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()
@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USERVARIABLETYPE])
@inject
async def create(
    request: Request,
    items: List[CreateUserVariableType] = Body(),
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    user_variable_types = await user_variable_type_service.create_all(items, tenant_id)
    result = ActionResult(success=True,items=user_variable_types)
    return result
    
@router.get("/{user_variable_type_id}", response_model=UserVariableType)
@authorize([ApiScopeType.QUERY_USERVARIABLETYPE])
@inject
async def find(
    request: Request,
    user_variable_type_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])):
    """UserVariableType bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    user_variable_type = await user_variable_type_service.get(user_variable_type_id, tenant_id,field_list)
    if not user_variable_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    return user_variable_type


@router.get("/", response_model=PagingResult[UserVariableType])
@authorize([ApiScopeType.QUERY_USERVARIABLETYPE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    user_variable_types: PagingResult[UserVariableType] = await user_variable_type_service.paging(
        query, tenant_id)  # type: ignore
    return user_variable_types


@router.put("/{user_variable_type_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USERVARIABLETYPE])
@inject
async def update(
    request: Request,
    user_variable_type_id: str,
    item: UpdateUserVariableType = Body(),
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    user_variable_type = await user_variable_type_service.update(user_variable_type_id, item, tenant_id)
    if not user_variable_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[user_variable_type], affected=1)
    return result

@router.put("/updateAll/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USERVARIABLETYPE])
@inject
async def updateAll(
    request: Request,
    query: QueryArgs = query_param(),
    item: UpdateAllUserVariableType = Body(),
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    count = len([sec for frst in query.where for sec in frst.value])  # type: ignore  
    updateCount = await user_variable_type_service.update_all(query, item, tenant_id)
    is_success = True if updateCount == count else False  
    result = ActionResult(success=is_success, affected=updateCount)
    return JSONResponse(content=result.model_dump())

@router.delete("/{user_variable_type_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USERVARIABLETYPE])
@inject
async def delete(
    request: Request,
    user_variable_type_id: UUID,
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    is_success = await user_variable_type_service.delete(user_variable_type_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USERVARIABLETYPE])
@inject
async def delete_by_ids(
    request: Request,
    user_variable_type_ids: List[str],
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await user_variable_type_service.delete_by_ids(user_variable_type_ids, tenant_id)
    is_success = True if deleted_count == len(user_variable_type_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USERVARIABLETYPE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    user_variable_type_service: UserVariableTypeService = Depends(
        Provide[AppContainer.user_variable_type_package.user_variable_type_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await user_variable_type_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())