from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.application.constants import ApiScopeType
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.application.content_page_template.content_page_template_model import CreateContentPageTemplate, ContentPageTemplate, UpdateContentPageTemplate, UpdateAllContentPageTemplate
from application.config.app_container import ApplicationContainer
from mapa.application.content_page_template.content_page_template_service import ContentPageTemplateService
from mapa.security import authorize

router = APIRouter()

@router.get("/{id}", response_model=ContentPageTemplate)
@authorize([ApiScopeType.QUERY_CONTENT_PAGE_TEMPLATE])
@inject
async def find(
    request: Request,
    id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])):
    """ContentPageTemplate bilgilerini getirir"""
    tenant_id = request.user.tenant_id
    content_page = await content_page_template_service.get(id, tenant_id, field_list)
    if not content_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return content_page


@router.get("/", response_model=PagingResult[ContentPageTemplate])
@authorize([ApiScopeType.QUERY_CONTENT_PAGE_TEMPLATE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])
):
    tenant_id = request.user.tenant_id
    content_pages: PagingResult[ContentPageTemplate] = await content_page_template_service.paging(
        query, tenant_id)  # type: ignore
    return content_pages


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTENT_PAGE_TEMPLATE])
@inject
async def create(
    request: Request,
    items: List[CreateContentPageTemplate] = Body(),
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])
):
    tenant_id = request.user.tenant_id
    content_pages = await content_page_template_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=content_pages)
    return result


@router.put("/{content_page_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTENT_PAGE_TEMPLATE])
@inject
async def update(
    request: Request,
    content_page_id: str,
    item: UpdateContentPageTemplate = Body(),
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])
):
    tenant_id = request.user.tenant_id
    content_page = await content_page_template_service.update(content_page_id, item, tenant_id)
    if content_page == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[content_page], affected=1)
    return result


@router.delete("/{content_page_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTENT_PAGE_TEMPLATE])
@inject
async def delete(
    request: Request,
    content_page_id: str,
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])
):
    tenant_id = request.user.tenant_id
    is_success = await content_page_template_service.delete(content_page_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTENT_PAGE_TEMPLATE])
@inject
async def delete_by_ids(
    request: Request,
    content_page_ids:  List[str],
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await content_page_template_service.delete_by_ids(content_page_ids, tenant_id)
    is_success = True if deleted_count == len(content_page_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONTENT_PAGE_TEMPLATE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    content_page_template_service: ContentPageTemplateService = Depends(
        Provide[ApplicationContainer.content_page_template_package.content_page_template_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await content_page_template_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
