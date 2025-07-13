from ctypes import Array
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.application.constants import ApiScopeType
from mapa.core.data.query_args import FilterOp, QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.application.app.app_model import CreateApp, App, ExportImportApp, UpdateApp, UpdateAllApp
from application.config.app_container import ApplicationContainer
from mapa.application.app.app_service import AppService
from mapa.core.data.base_entity import Base
from pydantic import BaseModel
from mapa.security import authorize

router = APIRouter()


@router.get("/applications", response_model=List[App])
@inject
async def applications(
    query: QueryArgs = query_param(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id_filter = [x for x in query.where if x.field == # type: ignore
                        'tenant_id' and x.op == FilterOp.EQUAL]  # type: ignore
    if tenant_id_filter is None or len(tenant_id_filter) == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(
            'Tenant_id filter must be singular and one'))
    # type: ignore
    apps: List[App] = await app_service.find(query, tenant_id_filter[0].value)# type: ignore
    return apps


@router.get("/export_applications")
@authorize([ApiScopeType.QUERY_APPLICATION])
@inject
async def export_applications(
    request: Request,
    query: QueryArgs = query_param(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    apps: List[ExportImportApp] = await app_service.export_applications(query, tenant_id)
    return apps


@router.post("/import_applications", response_model=ActionResult)
@authorize([ApiScopeType.QUERY_APPLICATION])
@inject
async def import_applications(
    request: Request,
    items: List[ExportImportApp] = Body(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    apps: List[ExportImportApp] = await app_service.import_applications(items, tenant_id)
    result = ActionResult(success=True)
    return JSONResponse(content=result.model_dump(mode='json'))


@router.get("/count")
@authorize([ApiScopeType.QUERY_APPLICATION])
@inject
async def count(
    request: Request,
    query: QueryArgs = query_param(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    count: int = await app_service.count(query, tenant_id)
    return count


@router.get("/{app_id}", response_model=App)
@authorize([ApiScopeType.QUERY_APPLICATION])
@inject
async def find(
    request: Request,
    app_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])):
    """App bilgilerini getirir"""
    tenant_id = request.user.tenant_id
    app = await app_service.get(app_id, tenant_id, field_list)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    return app


@router.get("/", response_model=PagingResult[App])
@authorize([ApiScopeType.QUERY_APPLICATION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    apps: PagingResult[App] = await app_service.paging(
        query, tenant_id)  # type: ignore
    return apps


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_APPLICATION])
@inject
async def create(
    request: Request,
    items: List[CreateApp] = Body(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    apps = await app_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=apps, affected=len(apps))
    return JSONResponse(content=result.model_dump(mode='json'))


@router.put("/{app_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_APPLICATION])
@inject
async def update(
    request: Request,
    app_id: str,
    item: UpdateApp = Body(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    app = await app_service.update(app_id, item, tenant_id)
    if app == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[app], affected=1)
    return result


@router.delete("/{app_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_APPLICATION])
@inject
async def delete(
    request: Request,
    app_id: str,
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    is_success = await app_service.delete(app_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump(mode='json'))


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_APPLICATION])
@inject
async def delete_by_ids(
    request: Request,
    app_ids: List[str],
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await app_service.delete_by_ids(app_ids, tenant_id)
    is_success = True if deleted_count == len(app_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump(mode='json'))


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_APPLICATION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    app_service: AppService = Depends(
        Provide[ApplicationContainer.app_package.app_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await app_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump(mode='json'))
