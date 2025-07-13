from typing import Any, Dict, List
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.constant import ApiScopeType
from mapa.gateway.context_var.context_var_model import ConvextVar, CreateConvextVar, UpdateConvextVar
from mapa.gateway.context_var.context_var_service import ContextVarService
from gateway.config.app_container import AppContainer
from mapa.security import authorize

router = APIRouter()

@router.get("/{context_var_id}", response_model=ConvextVar)
@authorize([ApiScopeType.QUERY_CONTEXT_VAR])
@inject
async def find(
    request: Request,
    context_var_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])):
    """Integration bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    integration = await context_var_service.get(context_var_id, tenant_id, field_list)
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return integration


@router.get("/", response_model=PagingResult[ConvextVar])
@authorize([ApiScopeType.QUERY_CONTEXT_VAR])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])
):
    tenant_id = request.user.tenant_id
    result: PagingResult[ConvextVar] = await context_var_service.paging(
        query, tenant_id)  # type: ignore
    return result


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTEXT_VAR])
@inject
async def create(
    request: Request,
    items: List[CreateConvextVar] = Body(),
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])
):
    tenant_id = request.user.tenant_id
    context_vars = await context_var_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=context_vars)
    return result


@router.put("/{context_var_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTEXT_VAR])
@inject
async def update(
    request: Request,
    context_var_id: str,
    item: UpdateConvextVar = Body(),
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])
):
    tenant_id = request.user.tenant_id
    context_var = await context_var_service.update(context_var_id, item, tenant_id)
    if context_var == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[context_var], affected=1)
    return result


@router.delete("/{context_var_id}", status_code=201, response_model=ActionResult)
@inject
async def delete(
    request: Request,
    context_var_id: str,
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])
):
    tenant_id = request.user.tenant_id
    is_success = await context_var_service.delete(context_var_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTEXT_VAR])
@inject
async def delete_by_ids(
    request: Request,
    context_var_ids: List[str],
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await context_var_service.delete_by_ids(context_var_ids, tenant_id)
    is_success = True if deleted_count == len(context_var_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTEXT_VAR])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    context_var_service: ContextVarService = Depends(
        Provide[AppContainer.context_var_package.context_var_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await context_var_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
