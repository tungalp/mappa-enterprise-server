import pytest
from mapa.sso.oidc.oidc_service import OidcService
from mapa.sso.oidc.response_handling.end_session_response import EndSessionResponse
from mapa.sso.oidc.response_handling.token_response import TokenResponse
from mapa.sso.oidc.results.end_session_result import EndSessionResult
from .oidc import create_service
from ..conftest import SsoFixture


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

@pytest.mark.asyncio
async def test_end_session(fixture: SsoFixture):
    """End Session"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    # Token oluşturulur.
    token_endpoint = fixture.create_token_auth_code_endpoint()
    token_response, error_response = await service.token(token_endpoint)
    
    end_session_endpoint = fixture.create_end_session_endpoint()
    end_session_endpoint.id_token_hint = token_response.id_token
    end_session_endpoint.state = None
    
    response = await service.end_session(end_session_endpoint, fixture.session_id)    
    
    assert response is not None
    assert isinstance(response, EndSessionResponse)
    
    result = EndSessionResult()
    ret_val = result.execute(response)
    
    assert ret_val is not None
    assert ret_val["url"] == end_session_endpoint.post_logout_redirect_uri
