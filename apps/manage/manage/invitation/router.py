from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from manage.config.app_container import AppContainer
from mapa.manage.invitation.invitation_model import CreateInvitation, Invitation, UpdateInvitation, UpdateAllInvitation
from mapa.manage.invitation.invitation_service import InvitationService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()

@router.get("/{invitation_id}", response_model=Invitation)
@authorize([ApiScopeType.QUERY_INVITATION])
@inject
async def get_by_invitation_id(
    request: Request,
    invitation_id: str,
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])):
    """Invitation bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    invitation = await invitation_service.get(invitation_id, tenant_id)
    if not invitation:
        return JSONResponse(status_code=404, content={
            "message": "Item not found"
        })

    return invitation


@router.get("/{id}", response_model=Invitation)
@authorize([ApiScopeType.QUERY_INVITATION])
@inject
async def find(
    request: Request,
    id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])):
    """Invitation bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    invitation = await invitation_service.get(id, tenant_id, field_list)
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return invitation


@router.get("/", response_model=PagingResult[Invitation])
@authorize([ApiScopeType.QUERY_INVITATION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    tenant_id = request.user.tenant_id
    invitations: PagingResult[Invitation] = await invitation_service.paging(
        query, tenant_id)  # type: ignore
    return invitations


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INVITATION])
@inject
async def create(
    request: Request,
    items: List[CreateInvitation] = Body(),
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    tenant_id = request.user.tenant_id
    invitations = await invitation_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=invitations)
    return result


@router.put("/{invitation_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INVITATION])
@inject
async def update(
    request: Request,
    invitation_id: str,
    item: UpdateInvitation = Body(),
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    tenant_id = request.user.tenant_id
    invitation = await invitation_service.update(invitation_id, item, tenant_id)
    if not invitation:
        return JSONResponse(status_code=404, content={
            "message": "Item not found"
        })
    result = ActionResult(success=True, items=[invitation], affected=1)
    return result


@router.delete("/{invitation_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INVITATION])
@inject
async def delete(
    request: Request,
    invitation_id: str,
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    tenant_id = request.user.tenant_id
    is_success = await invitation_service.delete(invitation_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INVITATION])
@inject
async def delete_by_ids(
    request: Request,
    invitation_ids:  List[str],
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await invitation_service.delete_by_ids(invitation_ids, tenant_id)
    is_success = True if deleted_count == len(invitation_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INVITATION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await invitation_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
