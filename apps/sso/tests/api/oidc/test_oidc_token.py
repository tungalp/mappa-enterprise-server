import pytest
from mapa.sso.oidc.oidc_service import OidcService
from mapa.sso.oidc.response_handling.token_response import TokenResponse
from .oidc import create_service
from ..conftest import SsoFixture


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

@pytest.mark.asyncio
async def test_token_auth_code(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    token_endpoint = fixture.create_token_auth_code_endpoint()
    response, error_response = await service.token(token_endpoint)
   
    assert response is not None
    assert isinstance(response, TokenResponse)
    assert error_response is None    
    
    
@pytest.mark.asyncio
async def test_token_refresh_token(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    token_endpoint = fixture.create_token_auth_code_endpoint()
    response, error_response = await service.token(token_endpoint)
    
    assert response is not None
    assert isinstance(response, TokenResponse)
    assert error_response is None
    assert response.refresh_token is not None
    refresh_token_endpoint = fixture.create_refresh_token_endpoint(response.refresh_token)
    
    response, error_response = await service.token(refresh_token_endpoint)
   
    assert response is not None
    assert isinstance(response, TokenResponse)
    assert error_response is None
    
    
@pytest.mark.asyncio
async def test_token_revoke_success(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    token_endpoint = fixture.create_token_auth_code_endpoint()
    response, error_response = await service.token(token_endpoint)
    
    assert response is not None
    assert isinstance(response, TokenResponse)
    assert error_response is None
    assert response.refresh_token is not None
    refresh_token_endpoint = fixture.create_refresh_token_endpoint(response.refresh_token)
    
    response, error_response = await service.token(refresh_token_endpoint)
   
    assert response is not None
    assert isinstance(response, TokenResponse)
    assert error_response is None
    
    # Revoke Token
    revocation_endpoint = fixture.create_revocation_endpoint(str(response.refresh_token))
    revoke_response = await service.revoke_token(revocation_endpoint)
    assert revoke_response is None