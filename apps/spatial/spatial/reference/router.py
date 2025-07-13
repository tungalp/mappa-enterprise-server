from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.reference.reference_model import (CreateReference, Reference,
                                                   UpdateReference)
from mapa.spatial.reference.reference_service import ReferenceService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{reference_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_REFERENCE])
@inject
async def find(
    request: Request,
    reference_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    reference = await reference_service.get(reference_id, tenant_id, field_list)
    if not reference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return reference


@router.get("/", response_model=PagingResult[Reference])
@authorize([ApiScopeType.QUERY_REFERENCE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])
):
    tenant_id = request.user.tenant_id
    references: PagingResult[Reference] = await reference_service.paging(
        query, tenant_id)  # type: ignore
    return references


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_REFERENCE])
@inject
async def create(
    request: Request,
    items: List[CreateReference] = Body(),
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])
):
    tenant_id = request.user.tenant_id
    references = await reference_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=references)
    return result


@router.put("/{reference_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_REFERENCE])
@inject
async def update(
    request: Request,
    reference_id: str,
    item: UpdateReference = Body(),
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])
):
    tenant_id = request.user.tenant_id
    reference = await reference_service.update(reference_id, item, tenant_id)
    if not reference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[reference], affected=1)
    return result


@router.delete("/{reference_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_REFERENCE])
@inject
async def delete(
    request: Request,
    reference_id: str,
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])
):
    tenant_id = request.user.tenant_id
    is_success = await reference_service.delete(reference_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_REFERENCE])
@inject
async def delete_by_ids(
    request: Request,
    reference_ids: List[str],
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await reference_service.delete_by_ids(reference_ids, tenant_id)
    is_success = True if deleted_count == len(reference_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_REFERENCE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    reference_service: ReferenceService = Depends(
        Provide[AppContainer.reference_package.reference_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await reference_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
