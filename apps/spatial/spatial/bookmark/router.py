from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.bookmark.bookmark_model import (Bookmark, CreateBookmark,
                                                 UpdateBookmark)
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.constant import ApiScopeType
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{bookmark_id}", response_model=Any)
# @authorize([ApiScopeType.QUERY_BOOKMARK])
@inject
async def find(
    request: Request,
    bookmark_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])):
    """Api bilgilerini getirir"""

    user_id = request.user.sub
    tenant_id = request.user.tenant_id
    bookmark = await bookmark_service.get(user_id, bookmark_id, tenant_id, field_list)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return bookmark


@router.get("/", response_model=PagingResult[Bookmark])
# @authorize([ApiScopeType.QUERY_BOOKMARK])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])
):
    tenant_id = request.user.tenant_id
    user_id = request.user.sub
    bookmarks: PagingResult[Bookmark] = await bookmark_service.paging(
                                                                      query,user_id,tenant_id)  # type: ignore
    return bookmarks


@router.post("/", status_code=201, response_model=ActionResult)
# @authorize([ApiScopeType.EDIT_BOOKMARK])
@inject
async def create(
    request: Request,
    items: List[CreateBookmark] = Body(),
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])
):
    tenant_id = request.user.tenant_id
    user_id = request.user.sub
    bookmarks = await bookmark_service.create_all(user_id, items, tenant_id)
    result = ActionResult(success=True, items=bookmarks)
    return result


@router.put("/{bookmark_id}", status_code=201, response_model=ActionResult)
# @authorize([ApiScopeType.EDIT_BOOKMARK])
@inject
async def update(
    request: Request,
    bookmark_id: str,
    item: UpdateBookmark = Body(),
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])
):
    tenant_id = request.user.tenant_id
    bookmark = await bookmark_service.update(bookmark_id, item, tenant_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[bookmark], affected=1)
    return result


@router.delete("/{bookmark_id}", status_code=201, response_model=ActionResult)
# @authorize([ApiScopeType.EDIT_BOOKMARK])
@inject
async def delete(
    request: Request,
    bookmark_id: str,
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])
):
    tenant_id = request.user.tenant_id
    is_success = await bookmark_service.delete(bookmark_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
# @authorize([ApiScopeType.EDIT_BOOKMARK])
@inject
async def delete_by_ids(
    request: Request,
    bookmark_ids: List[str],
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await bookmark_service.delete_by_ids(bookmark_ids, tenant_id)
    is_success = True if deleted_count == len(bookmark_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
# @authorize([ApiScopeType.EDIT_BOOKMARK])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    bookmark_service: BookmarkService = Depends(
        Provide[AppContainer.bookmark_package.bookmark_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await bookmark_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
