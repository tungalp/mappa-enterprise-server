from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.namespace.namespace_model import (CreateNamespace, Namespace,
                                                   UpdateNamespace)
from mapa.spatial.namespace.namespace_service import NamespaceService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{namespace_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_NAMESPACE])
@inject
async def find(
    request: Request,
    namespace_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    namespace = await namespace_service.get(namespace_id, tenant_id, field_list)
    if not namespace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return namespace


@router.get("/", response_model=PagingResult[Namespace])
@authorize([ApiScopeType.QUERY_NAMESPACE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])
):
    tenant_id = request.user.tenant_id
    namespaces: PagingResult[Namespace] = await namespace_service.paging(
        query, tenant_id)  # type: ignore
    return namespaces


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_NAMESPACE])
@inject
async def create(
    request: Request,
    items: List[CreateNamespace] = Body(),
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])
):
    tenant_id = request.user.tenant_id
    namespaces = await namespace_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=namespaces)
    return result


@router.put("/{namespace_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_NAMESPACE])
@inject
async def update(
    request: Request,
    namespace_id: str,
    item: UpdateNamespace = Body(),
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])
):
    tenant_id = request.user.tenant_id
    namespace = await namespace_service.update(namespace_id, item, tenant_id)
    if not namespace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[namespace], affected=1)
    return result


@router.delete("/{namespace_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_NAMESPACE])
@inject
async def delete(
    request: Request,
    namespace_id: str,
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])
):
    tenant_id = request.user.tenant_id
    is_success = await namespace_service.delete(namespace_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_NAMESPACE])
@inject
async def delete_by_ids(
    request: Request,
    namespace_ids: List[str],
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await namespace_service.delete_by_ids(namespace_ids, tenant_id)
    is_success = True if deleted_count == len(namespace_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_NAMESPACE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    namespace_service: NamespaceService = Depends(
        Provide[AppContainer.namespace_package.namespace_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await namespace_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
