from datetime import datetime
from typing import Any
from uuid import UUID

from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.sso.auth.interaction_service import InteractionService
from mapa.sso.auth.mail_service import MailService
from mapa.sso.auth.new_password_endpoint import NewPasswordEndpoint
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.sso.oidc.response_handling.authorize_response_handler import AuthorizeResponseHandler
from mapa.sso.oidc.results.authorize_result import AuthorizeResult
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import APIKeyCookie
from dependency_injector.wiring import Provide, inject
from mapa.sso.auth.auth_service import AuthService
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.sso.constants import SsoConstants
from sso.config.app_container import AppContainer
from mapa.sso.auth.forgot_password_endpoint import ForgotPasswordEndpoint

router = APIRouter()

session_cookie = APIKeyCookie(
    name=SsoConstants.SESSION_COOKIE_NAME, auto_error=False
)


@router.post("/register")
@inject
async def post_register(
    request: Request,
    register_endpoint: RegisterEndpoint,
    config: Any = Depends(Provide[AppContainer.config]),
    auth_service: AuthService = Depends(
        Provide[AppContainer.auth_package.auth_service]),
    interaction_service: InteractionService = Depends(
        Provide[AppContainer.oidc_package.interaction_service]),
    authorize_handler: AuthorizeResponseHandler = Depends(
        Provide[AppContainer.oidc_package.authorize_handler]),
):
    """Yeni bir kullanıcı oluşturur"""
    session_id = request.session.get("id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    auth_result = AuthorizeResult(config["oidc"]["app_host"])
    tenant_id, user_session, auth_request = await auth_service.register(UUID(session_id), register_endpoint)
    # Kullanıcı yetkilendirildiyse consent kontrol edilir.
    if user_session.authenticated:
        request.session.update({
            "id": str(user_session.id),
            "tenant_id": str(tenant_id),
            "issued_at": datetime.utcnow().timestamp()
        })
        consent_response = await interaction_service.process_consent(auth_request)
        # Eğer consent ihtiyacı varsa consent sayfasına yönlendirilir.
        if consent_response:
            response_dict = auth_result.execute_login(
                register_endpoint, consent_response)
        else:
            # Consent ihtiyacı yoksa MFA kontrol edilir. (TODO) tamamlanacak
            mfa_response = await interaction_service.process_mfa(auth_request)
            if mfa_response:
                response_dict = auth_result.execute_login(
                    register_endpoint, mfa_response)
            else:
                # Herhangi bir interaction bulunamadı ise authorize işlemi döndürülür.
                authorize_response = await authorize_handler.create_response(auth_request)
                response_dict = auth_result.execute(
                    register_endpoint, authorize_response)

        return JSONResponse(status_code=status.HTTP_200_OK, content=response_dict["url"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not authenticated")


# @router.get("/login/{client_id}", status_code=302)
# @inject
# async def get_login(
#     client_id: str,
#     redirect_uri: str,
#     auth_util_service: AuthUtilService = Depends(
#         Provide[AppContainer.auth_package.auth_util_service])):
#     """Authorize servisine yönlendirir."""

#     try:
#         result = await auth_util_service.create_authorize_redirect(client_id, redirect_uri)
#     except Exception as ex:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex

#     return RedirectResponse(result["url"], 302)


@router.post("/login")
@inject
async def post_login(
    request: Request,
    login_endpoint: LoginEndpoint,
    config: Any = Depends(Provide[AppContainer.config]),
    auth_service: AuthService = Depends(
        Provide[AppContainer.auth_package.auth_service]),
    interaction_service: InteractionService = Depends(
        Provide[AppContainer.oidc_package.interaction_service]),
    authorize_handler: AuthorizeResponseHandler = Depends(
        Provide[AppContainer.oidc_package.authorize_handler]),
):
    """Yeni bir kullanıcı oturumu açar ya da varolanı günceller"""

    session_id = request.session.get("id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    auth_result = AuthorizeResult(config["oidc"]["app_host"])
    try:
        tenant_id, user_session, auth_request = await auth_service.login(UUID(session_id), login_endpoint)
    except ValueError as ex:
        raise ValueError(ex)
    except HTTPException as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not authenticated")

    # Kullanıcı yetkilendirildiyse consent kontrol edilir.
    if user_session.authenticated:
        request.session.update({
            "id": str(user_session.id),
            "issued_at": datetime.utcnow().timestamp(),
            "tenant_id": str(tenant_id)
        })
        consent_response = await interaction_service.process_consent(auth_request)
        # Eğer consent ihtiyacı varsa consent sayfasına yönlendirilir.
        if consent_response:
            response_dict = auth_result.execute_login(
                login_endpoint, consent_response)
        else:
            # Consent ihtiyacı yoksa MFA kontrol edilir. (TODO) tamamlanacak
            mfa_response = await interaction_service.process_mfa(auth_request)
            if mfa_response:
                response_dict = auth_result.execute_login(
                    login_endpoint, mfa_response)
            else:
                # Herhangi bir interaction bulunamadı ise authorize işlemi döndürülür.
                authorize_response = await authorize_handler.create_response(auth_request)
                response_dict = auth_result.execute(
                    login_endpoint, authorize_response)

        return JSONResponse(status_code=status.HTTP_200_OK, content=response_dict["url"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not authenticated")


@router.post("/consent")
@inject
async def post_consent(
    request: Request,
    consent_endpoint: ConsentEndpoint,
    config: Any = Depends(Provide[AppContainer.config]),
    auth_service: AuthService = Depends(
        Provide[AppContainer.auth_package.auth_service]),
    interaction_service: InteractionService = Depends(
        Provide[AppContainer.oidc_package.interaction_service]),
    authorize_handler: AuthorizeResponseHandler = Depends(
        Provide[AppContainer.oidc_package.authorize_handler])
):
    """Kullanıcı onayı kaydedilir."""

    session_id = request.session.get("id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    auth_result = AuthorizeResult(config["oidc"]["app_host"])
    consent, auth_request = await auth_service.consent(UUID(session_id), consent_endpoint)
    if consent.accepted:
        mfa_response = await interaction_service.process_mfa(auth_request)
        if mfa_response:
            response_dict = auth_result.execute_consent(
                consent_endpoint, mfa_response)
        else:
            # Herhangi bir interaction bulunamadı ise authorize işlemi döndürülür.
            authorize_response = await authorize_handler.create_response(auth_request)
            response_dict = auth_result.execute(
                consent_endpoint, authorize_response)

        return JSONResponse(status_code=status.HTTP_200_OK, content=response_dict["url"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not authenticated")


@router.post("/forgot-password", status_code=200)
@inject
async def post_forgot_password(
    forgot_password_endpoint: ForgotPasswordEndpoint,
    config: Any = Depends(Provide[AppContainer.config]),
    auth_util_service: AuthUtilService = Depends(
        Provide[AppContainer.oidc_package.util_service]),
    mail_service: MailService = Depends(
        Provide[AppContainer.auth_package.mail_service]),
    service_messenger: ServiceMessenger = Depends(Provide[AppContainer.service_messenger]),
):
    """Kullanıcıya yeni şifre gitmek için link gönderir."""

    user = await service_messenger.user_get_by_email(forgot_password_endpoint.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=forgot_password_endpoint.email)

    response_dict = auth_util_service.create_new_password_link(
        config["oidc"]["app_host"], forgot_password_endpoint)
    await mail_service.send_forgot_password(forgot_password_endpoint.email, response_dict["url"], forgot_password_endpoint.lang)

    return JSONResponse(content={})


@router.post("/new-password", status_code=200)
@inject
async def post_new_password(
    new_password_endpoint: NewPasswordEndpoint,
    auth_service: AuthService = Depends(
        Provide[AppContainer.auth_package.auth_service]),

):
    """Kullanıcının şifresini yeni şifre ile değiştirir."""

    try:
        user = await auth_service.new_password(new_password_endpoint)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex

    return JSONResponse(content={})
