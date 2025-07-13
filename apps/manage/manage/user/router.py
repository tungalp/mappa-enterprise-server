from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser
from fastapi.responses import RedirectResponse, JSONResponse
from dependency_injector.wiring import Provide, inject
from mapa.manage.invitation.invitation_endpoint import InvitationEndpoint
from mapa.manage.invitation.invitation_model import CreateInvitation, UpdateInvitation
from mapa.manage.invitation.invitation_service import InvitationService
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.constants import ApiScopeType, PromptModes
from mapa.manage.invitation.invitation_util_service import InvitationUtilService
from mapa.manage.invitation.mail_service import MailService
from mapa.manage.user.user_model import CreateUser, User, UpdateAllUser, UpdateUser
from manage.config.app_container import AppContainer
from mapa.manage.user.user_service import UserService
from mapa.security import authorize

router = APIRouter()


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.QUERY_USER])
@inject
async def create(
    request: Request,
    items: List[CreateUser] = Body(),
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])
):
    tenant_id = request.user.tenant_id
    users = await user_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=users)
    return result


@router.get("/{user_id}", response_model=User)
@authorize([ApiScopeType.QUERY_USER])
@inject
async def find(
    request: Request,
    user_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])):
    """User bilgilerini getirir"""
    tenant_id = request.user.tenant_id
    user = await user_service.get(user_id, tenant_id, field_list)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return user


@router.get("/", response_model=PagingResult[User])
@authorize([ApiScopeType.QUERY_USER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])
):
    tenant_id = request.user.tenant_id
    users: PagingResult[User] = await user_service.paging(
        query, tenant_id)  # type: ignore
    return users


@router.put("/{user_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USER])
@inject
async def update(
    request: Request,
    user_id: str,
    item: UpdateUser = Body(),
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])
):
    tenant_id = request.user.tenant_id
    user = await user_service.update(user_id, item, tenant_id)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[user], affected=1)
    return result


@router.put("/updateAll/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USER])
@inject
async def updateAll(
    request: Request,
    query: QueryArgs = query_param(),
    item: UpdateAllUser = Body(),
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])
):
    tenant_id = request.user.tenant_id
    # type: ignore
    count = len([sec for frst in query.where for sec in frst.value])
    updateCount = await user_service.update_all(query, item, tenant_id)
    is_success = True if updateCount == count else False
    result = ActionResult(success=is_success, affected=updateCount)
    return JSONResponse(content=result.model_dump())

# @router.put("/", status_code=201, response_model=ActionResult)
# @inject
# async def update_by_ids(
#     user_ids: Any= Body(),
#     user_service: UserService = Depends(
#         Provide[AppContainer.user_package.user_service])
# ):
#     ids : List[str] = [obj for obj in (body['data']['ids'])]
#     item : UpdateUser = (body['data']['updateAllEntity'])

#     user = await user_service.update_by_ids(Any,Any, tenant_id)
#     result = ActionResult(success=True, items=[user], affected=1)
#     return JSONResponse(content=result.model_dump())


@router.delete("/{user_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USER])
@inject
async def delete(
    request: Request,
    user_id: UUID,
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])
):
    tenant_id = request.user.tenant_id
    is_success = await user_service.delete(user_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USER])
@inject
async def delete_by_ids(
    request: Request,
    user_ids: List[str],
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await user_service.delete_by_ids(user_ids, tenant_id)
    is_success = True if deleted_count == len(user_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_USER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    user_service: UserService = Depends(
        Provide[AppContainer.user_package.user_service]), 
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
   
    tenant_id = request.user.tenant_id
    users = await user_service.paging(query, tenant_id)
    
    if(users and len(users.items) > 0):
        await invitation_service.delete_user_info(users.items,tenant_id)
       
    deleted_count = await user_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.post("/invitation")
@authorize([ApiScopeType.QUERY_INVITATION])
@inject
async def user_invitation(
    request: Request,
    datas: List[InvitationEndpoint],
    config: Any = Depends(Provide[AppContainer.config]),
    invitation_util_service: InvitationUtilService = Depends(
        Provide[AppContainer.invitation_package.invitation_util_service]),
    mail_service: MailService = Depends(
        Provide[AppContainer.invitation_package.mail_service]),
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service]),
):

    user_id = request.user.sub
    tenant_id = request.user.tenant_id

    for data in datas:
        invitation = await invitation_service.create(CreateInvitation(
            user_id=user_id,
            email=data.email,
            expired_at=datetime.now(),
            tenant=tenant_id,
            organization_id=data.organization_id # type: ignore   
        ),tenant_id)

        response_dict = await invitation_util_service.create_invitation_link(
            config["oidc"]["app_host"], invitation)

        await mail_service.send_register_email(data.email, response_dict["url"], data.lang)

    return JSONResponse(content={})


@router.get("/invitation-redirect/")
@inject
async def get_user_invitation(
    request: Request,
    config: Any = Depends(Provide[AppContainer.config]),
    invitation_util_service: InvitationUtilService = Depends(
        Provide[AppContainer.invitation_package.invitation_util_service]), 
    invitation_service: InvitationService = Depends(
        Provide[AppContainer.invitation_package.invitation_service])
):
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token notfound")

    result_inv = await invitation_util_service.check_invitation(token)
    invitation = await invitation_service.get(result_inv["invitation_id"],tenant_id=result_inv["tenant_id"])

    # Eğer kullanıcı davet usulü ile geldiyse ekstra olarak davet sırasında seçilen organization'a user olarak eklenir. (04.03.2023)
    if result_inv["screen_hint"] == PromptModes.LOGIN and invitation.organization_id:
        # organization_user_member = await invitation_util_service._organization_user_service.create(CreateOrganizationUser(  
        #     user_id = result_inv["user_id"],
        #     organization_id = invitation.organization_id
        # ), tenant_id=str(invitation.tenant))
        invitation_updated = await invitation_service.update(invitation.id,UpdateInvitation(used=True,organization_id=invitation.organization_id), tenant_id=str(invitation.tenant))

    result = invitation_util_service.create_invitation_link_redirect(
        config["oidc"]["app_host"],
        result_inv["screen_hint"],
        result_inv["invitation_id"],
        result_inv["email"])

    return RedirectResponse(result["url"], 302)

# test için yazıldı. silinecek
# @router.get("/user-scopes/client_id={client_id}&user_id={user_id}")
# @inject
# async def user_scopes(
#     client_id: str,
#     user_id: str,
#     request: Request,
#     user_service: UserService = Depends(
#         Provide[AppContainer.user_package.user_service])
# ):
#     # user_id = request.user.sub
#     tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"
#     user_scopes = await user_service.get_user_scopes(user_id, client_id, tenant_id)
#     return user_scopes
