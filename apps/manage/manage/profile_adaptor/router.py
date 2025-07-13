from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.profile_adaptor.profile_adaptor_model import CreateProfileAdaptor, ProfileAdaptor, UpdateAllProfileAdaptor, UpdateProfileAdaptor
from manage.config.app_container import AppContainer
from mapa.manage.profile_adaptor.profile_adaptor_service import ProfileAdaptorService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()

@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PROFILE_ADAPTOR])
@inject
async def create(
    request: Request,
    items: List[CreateProfileAdaptor] = Body(),
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])
):
    tenant_id = request.user.tenant_id
    profile_adaptors = await profile_adaptor_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=profile_adaptors)
    return result


@router.get("/{profile_adaptor_id}", response_model=ProfileAdaptor)
@authorize([ApiScopeType.QUERY_PROFILE_ADAPTOR])
@inject
async def find(
    request: Request,
    profile_adaptor_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])):
    """ProfileAdaptor bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    profile_adaptor = await profile_adaptor_service.get(profile_adaptor_id, tenant_id, field_list)
    if not profile_adaptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return profile_adaptor


@router.get("/", response_model=PagingResult[ProfileAdaptor])
@authorize([ApiScopeType.QUERY_PROFILE_ADAPTOR])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])
):
    tenant_id = request.user.tenant_id
    profile_adaptors: PagingResult[ProfileAdaptor] = await profile_adaptor_service.paging(
        query, tenant_id)  # type: ignore
    return profile_adaptors


@router.put("/{profile_adaptor_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PROFILE_ADAPTOR])
@inject
async def update(
    request: Request,
    profile_adaptor_id: str,
    item: UpdateProfileAdaptor = Body(),
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])
):
    tenant_id = request.user.tenant_id
    profile_adaptor = await profile_adaptor_service.update(profile_adaptor_id, item, tenant_id)
    if not profile_adaptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[profile_adaptor], affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/{profile_adaptor_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PROFILE_ADAPTOR])
@inject
async def delete(
    request: Request,
    profile_adaptor_id: UUID,
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])
):
    tenant_id = request.user.tenant_id
    is_success = await profile_adaptor_service.delete(profile_adaptor_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/{profile_adaptors_ids}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PROFILE_ADAPTOR])
@inject
async def delete_by_ids(
    request: Request,
    profile_adaptors_ids: Any,
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await profile_adaptor_service.delete_by_ids(profile_adaptors_ids, tenant_id)
    is_success = True if deleted_count == len(profile_adaptors_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PROFILE_ADAPTOR])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    profile_adaptor_service: ProfileAdaptorService = Depends(
        Provide[AppContainer.profile_adaptor_package.profile_adaptor_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await profile_adaptor_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
