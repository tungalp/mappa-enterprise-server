from uuid import UUID
from fastapi.responses import RedirectResponse, HTMLResponse
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from mapa.sso.oidc.oidc_service import OidcService
from mapa.sso.oidc.results.authorize_result import AuthorizeResult


async def authorize(
    app_host: str,
    authorize_endpoint: AuthorizeEndpoint,
    session_id: UUID | None,
    oidc_service: OidcService):
    """Kimliklendirme"""

    # Yetkilendirme işlemi yapılır. Gelen isteğin parametrelerine göre Dönüş değeri oluşturulur
    auth_response, error_response = await oidc_service.authorize(authorize_endpoint, session_id)
    auth_result = AuthorizeResult(app_host)

    # Dönüş değeri hazırlanır
    if auth_response:
        response_dict = auth_result.execute(authorize_endpoint, auth_response)
    elif error_response:
        response_dict = auth_result.execute_error(authorize_endpoint, error_response)
    else:
        raise ValueError("Authorization Response Error")

    response = None
    if response_dict["type"] == "redirect":
        response = RedirectResponse(response_dict["url"], 302)
    else:
        response = HTMLResponse(response_dict["content"])

    return response