from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.manage.constants import ApiScopeType
from mapa.manage.ldap_server.ldap_server_model import (
    CreateLdapServer,
    LdapServer,
    UpdateLdapServer,
)
from mapa.manage.ldap_server.ldap_server_service import LdapServerService
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from manage.config.app_container import AppContainer

router = APIRouter()


@router.get("/{ldap_server_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_LDAP_SERVER])
@inject
async def find(
    request: Request,
    ldap_server_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    """LdapServer bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    ldap_server = await ldap_server_service.get(ldap_server_id, tenant_id, field_list)
    ldap_server.password = None
    if not ldap_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Item Not Found")
        )

    return ldap_server


@router.get("/", response_model=PagingResult[LdapServer])
@authorize([ApiScopeType.QUERY_LDAP_SERVER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    tenant_id = request.user.tenant_id
    ldap_servers: PagingResult[LdapServer] = await ldap_server_service.paging(
        query, tenant_id
    )  # type: ignore
    return ldap_servers


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LDAP_SERVER])
@inject
async def create(
    request: Request,
    items: List[CreateLdapServer] = Body(),
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    tenant_id = request.user.tenant_id
    ldap_servers = await ldap_server_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=ldap_servers)
    return result


@router.put("/{ldap_server_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LDAP_SERVER])
@inject
async def update(
    request: Request,
    ldap_server_id: str,
    item: UpdateLdapServer = Body(),
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    tenant_id = request.user.tenant_id
    ldap_server = await ldap_server_service.update(ldap_server_id, item, tenant_id)
    if not ldap_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Item Not Found")
        )
    result = ActionResult(success=True, items=[ldap_server], affected=1)
    return result


@router.delete("/{ldap_server_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LDAP_SERVER])
@inject
async def delete(
    request: Request,
    ldap_server_id: str,
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    tenant_id = request.user.tenant_id
    is_success = await ldap_server_service.delete(ldap_server_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Item Not Found")
        )
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LDAP_SERVER])
@inject
async def delete_by_ids(
    request: Request,
    ldap_server_ids: List[str],
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    tenant_id = request.user.tenant_id
    deleted_count = await ldap_server_service.delete_by_ids(ldap_server_ids, tenant_id)
    is_success = True if deleted_count == len(ldap_server_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Item Not Found")
        )
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LDAP_SERVER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    tenant_id = request.user.tenant_id
    deleted_count = await ldap_server_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())

@router.get("/check_connection/{ldap_server_id}", response_model=ActionResult)
@authorize([ApiScopeType.QUERY_LDAP_SERVER])
@inject
async def check_connection(
    request: Request,
    ldap_server_id: str,
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    """LdapServer bilgilerini getirir"""
    tenant_id = request.user.tenant_id
    is_connected = await ldap_server_service.check_ldap_connection(ldap_server_id, tenant_id)
    result = ActionResult(success=is_connected)
    return JSONResponse(content=result.model_dump())


@router.get("/start_sync/{ldap_server_id}", response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LDAP_SERVER])
@inject
async def start_sync(
    request: Request,
    ldap_server_id: str,
    ldap_server_service: LdapServerService = Depends(
        Provide[AppContainer.ldap_server_package.ldap_server_service]
    ),
):
    """LdapServer bilgilerini getirir"""
    tenant_id = request.user.tenant_id
    is_success = await ldap_server_service.start_sync(ldap_server_id, tenant_id)
    result = ActionResult(success=is_success)
    return JSONResponse(content=result.model_dump())
