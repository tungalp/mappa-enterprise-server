from typing import Any
from uuid import UUID
from mapa.core.data.result import ActionResult
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.sso.oidc.token_service import TokenService
from mapa.sso.user_session_client.user_session_client_model import UpdateUserSessionClient
from mapa.sso.user_session_client.user_session_client_service import UserSessionClientService
from sso.config.app_container import AppContainer

router = APIRouter()

token_auth_scheme = HTTPBearer()


@router.post("/", status_code=200, response_model=ActionResult)
@inject
async def change_tenant(
    request: Request,
    item: Any = Body(),
    messenger: ServiceMessenger = Depends(
        Provide[AppContainer.service_messenger]),
    user_session_client_service: UserSessionClientService = Depends(
        Provide[AppContainer.user_session_package.user_session_client_service]),
    token_service: TokenService = Depends(
        Provide[AppContainer.oidc_package.token_service])
):
    token = await token_auth_scheme(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str("Token not found"))
    decode_token = await token_service.decode_token(token.credentials)

    session_id = request.session.get("id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str('Session Not Found'))

    tenant_id = item.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Tenant Not Found'))

    client_id = item.get("client_id")
    client = await messenger.get_client_by_client_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Client Not Found'))

    session_client = await user_session_client_service.find_by_client(UUID(session_id), client["id"])
    if not session_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str('UserSesionClient Not Found'))

    user_session_client = await user_session_client_service.update(session_client.id, UpdateUserSessionClient(
        tenant=UUID(tenant_id)
    ))
    result = ActionResult(success=user_session_client is not None, items=[])
    return result
