from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4
from jwcrypto.jwk import JWK
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.constants import ProtocolRoutePaths
from mapa.sso.jwk.jwk_service import JwkService
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from dependency_injector.wiring import Provide, inject
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from mapa.sso.oidc.end_points.end_session import EndSessionEndpoint
from mapa.sso.oidc.end_points.revocation import RevocationEndpoint
from mapa.sso.oidc.end_points.token import TokenEndpoint
from mapa.sso.oidc.response_handling.end_session_response import EndSessionResponse
from mapa.sso.oidc.results.end_session_result import EndSessionResult
from mapa.sso.oidc.token_service import TokenService
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService
from sso.config.app_container import AppContainer
from mapa.sso.oidc.oidc_service import OidcService
from .authorize import authorize


router = APIRouter()

security = HTTPBasic(auto_error=False)
token_auth_scheme = HTTPBearer()

def set_session(request: Request):
    """Kullanıcı oturum bilgilerini set eder"""
    if not request.session.get("id"):
        request.session["id"] = str(uuid4())
        request.session["created"] = datetime.utcnow().timestamp()
                
@router.post("/authorize")
@inject
async def authorize_post(
    request: Request,
    config: Any = Depends(Provide[AppContainer.config]),
    oidc_service: OidcService = Depends(
        Provide[AppContainer.oidc_package.oidc_service])
):
    """OIDC authorize"""
    try:
        authorize_endpoint = AuthorizeEndpoint(**vars(await request.form())["_dict"])
        session_id = request.session.get("id")
        session_uuid = UUID(session_id) if session_id else None
        ret_val = await authorize(config["oidc"]["app_host"], authorize_endpoint, session_uuid, oidc_service)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex
    finally:
        set_session(request)

    return ret_val


@router.get("/authorize")
@inject
async def authorize_get(
    request: Request,
    config: Any = Depends(Provide[AppContainer.config]),
    authorize_endpoint: AuthorizeEndpoint = Depends(AuthorizeEndpoint),
    oidc_service: OidcService = Depends(
        Provide[AppContainer.oidc_package.oidc_service])
):
    """OIDC authorize"""
    try:
        session_id = request.session.get("id")
        session_uuid = UUID(session_id) if session_id else None
        ret_val = await authorize(config["oidc"]["app_host"], authorize_endpoint, session_uuid, oidc_service)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex
    finally:
        set_session(request)

    return ret_val


@router.post("/token")
@inject
async def create_token(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
    oidc_service: OidcService = Depends(
        Provide[AppContainer.oidc_package.oidc_service])
):
    """OIDC token"""
    try:
        token_endpoint = TokenEndpoint(**vars(await request.form())["_dict"])
        # Eğer basic authentication kullanılmışsa client_id ve client_secret bilgileri alınır.
        if credentials:
            token_endpoint.client_id = credentials.username
            token_endpoint.client_secret = credentials.password

        auth_response, error_response = await oidc_service.token(token_endpoint)
        if error_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error_response.error_description))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex

    return auth_response


@router.post("/revocation")
@inject
async def revocate_token(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
    oidc_service: OidcService = Depends(
        Provide[AppContainer.oidc_package.oidc_service])
):
    """OIDC token"""
    
    revocation_endpoint = RevocationEndpoint(**vars(await request.form())["_dict"])
    # Eğer basic authentication kullanılmışsa client_id ve client_secret bilgileri alınır.
    if credentials:
        revocation_endpoint.client_id = credentials.username
        revocation_endpoint.client_secret = credentials.password

    error_response = await oidc_service.revoke_token(revocation_endpoint)
    if error_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error_response.error_description))

    return JSONResponse(content={})


@router.get("/endsession")
@inject
async def endsession(
    request: Request,
    end_session_endpoint: EndSessionEndpoint = Depends(EndSessionEndpoint),
    oidc_service: OidcService = Depends(
        Provide[AppContainer.oidc_package.oidc_service])
):
    """OIDC End Session"""
    try:
        session_id = request.session.get("id")
        session_uuid = UUID(session_id) if session_id else None
        if not session_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="session not found")

        end_session_response = await oidc_service.end_session(end_session_endpoint, session_uuid)
        end_session_result = EndSessionResult()

        # Dönüş değeri hazırlanır
        if isinstance(end_session_response, EndSessionResponse):
            response_dict = end_session_result.execute(end_session_response)
        else:
            response_dict = end_session_result.execute_error(end_session_endpoint, end_session_response)

        return RedirectResponse(response_dict["url"], 302)
        
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex
    finally:
        set_session(request)


@router.get("/userinfo")
@inject
async def userinfo(
    request: Request,
    token_service: TokenService = Depends(Provide[AppContainer.oidc_package.token_service]),
    service_messenger: ServiceMessenger = Depends(Provide[AppContainer.service_messenger]),
):
    """OIDC authorize"""

    token = await token_auth_scheme(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str("Token not found"))
    decode_token = await token_service.decode_token(token.credentials)
    user_id = decode_token.get("sub")
    tenant_id = decode_token.get("tenant_id")
    user = await service_messenger.get_by_user_id(str(user_id), [], str(tenant_id))
    # UserInfo içerisine kullanıcının organization bilgilerini bulup ekler (04.03.2024)
    query_args_organization: QueryArgs = QueryArgs(
                where=[
                    Filter(field="id", op=FilterOp.EQUAL, value=user_id),
                    ],
                select=[
                        "id", "name", "surname", "email", "password", "email_verified", "phone", "context", "subject_id", "created_at",
                        "organizations.id","organizations.name","organizations.description","organizations.integration_id"
                    ],
                limit=0,
                offset=0
            )
     
    user_organizations = await service_messenger.user_find(query_args_organization.to_serialize(),tenant_id)
    filtered_organizations = []
    if user_organizations is not None and len(user_organizations) == 1 and user_organizations[0]["organizations"] is not None and len(user_organizations[0]["organizations"]) > 0:
        for organization in user_organizations[0]["organizations"]:
            filtered_organizations.append({
                "id": organization["id"],
                "name": organization["name"],
                "description": organization["description"],
                "integration_id": organization["integration_id"],
            })
    # end of UserInfo içerisine kullanıcının organization bilgilerini bulup ekler (04.03.2024)
            
    return {
        "id": user["id"],
        "name": user["name"],
        "given_name": user["given_name"],
        "family_name": user["family_name"],
        "nickname": user["nickname"],
        "email": user["email"],
        "email_verified": user["email_verified"],
        "phone": user["phone"],
        "address": user["address"],
        "picture": user["picture"],
        "organizations": filtered_organizations
    }
    
@router.get("/jwks")
@inject
async def jwks_json(
    jwk_service: JwkService = Depends(Provide[AppContainer.oidc_package.jwk_service])
):
    """OIDC JWKS"""
    try:
        jwk_list = await jwk_service.get_active_set()
        ret_val = {
            "keys": [jwk_model.jwk for jwk_model in jwk_list]
        }
        return JSONResponse(content=ret_val)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex


@router.get("/.well-known/openid-configuration")
@inject
async def get_oidc_config(
    # request: Request,
    config: Any = Depends(Provide[AppContainer.config])
):
    """OIDC Well Known Configuration"""
    try:
        oidc_config = config["oidc"]
        issuer: str = oidc_config["issuer"]
        ret_val = {
            "issuer": oidc_config["issuer"],
            "authorization_endpoint": issuer + "/" + ProtocolRoutePaths.AUTHORIZE,
            "device_authorization_endpoint": issuer + "/" + ProtocolRoutePaths.DEVICE_AUTHORIZATION,
            "token_endpoint": issuer + "/" + ProtocolRoutePaths.TOKEN,
            "userinfo_endpoint": issuer + "/" + ProtocolRoutePaths.USERINFO,
            "revocation_endpoint": issuer + "/" + ProtocolRoutePaths.REVOCATION,
            "jwks_uri": issuer + "/" + ProtocolRoutePaths.DISCOVERY_WEB_KEYS,
            "response_types_supported": [
                "code",
                "token",
                "id_token",
                "code token",
                "code id_token",
                "token id_token",
                "code token id_token",
                "none"
            ],
            "subject_types_supported": [
                "public"
            ],
            "id_token_signing_alg_values_supported": [
                "RS256"
            ],
            "scopes_supported": [
                "openid",
                "email",
                "profile"
            ],
            "token_endpoint_auth_methods_supported": [
                "client_secret_post",
                "client_secret_basic"
            ],
            "claims_supported": [
                "aud",
                "email",
                "email_verified",
                "exp",
                "family_name",
                "given_name",
                "iat",
                "iss",
                "locale",
                "name",
                "picture",
                "sub"
            ],
            "code_challenge_methods_supported": [
                "plain",
                "S256"
            ],
            "grant_types_supported": [
                "authorization_code",
                "refresh_token",
                "urn:ietf:params:oauth:grant-type:device_code",
                "urn:ietf:params:oauth:grant-type:jwt-bearer"
            ]              
        }
        return JSONResponse(content=ret_val)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex)) from ex
