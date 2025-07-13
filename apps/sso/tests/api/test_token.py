from random import random
import pytest
from mapa.sso.jwk.jwk_service import JwkService

from mapa.sso.oidc.token_service import CreateToken, TokenService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> TokenService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    jwk_service = JwkService(async_db)

    return TokenService(
        fixture.issuer,
        jwk_service
    )


@pytest.mark.asyncio
async def test_create_access_token(fixture: SsoFixture):
    """Service"""

    service: TokenService = await create_service(fixture)
    assert service is not None
    
    create_token = CreateToken(
        audience="http://test.api",
        client_id="client_id_manage",
        tenant_id=fixture.tenant_id,
        user_id=fixture.user_id
    )
    access_token = await service.create_access_token(create_token, "openid", [], 10000)
    assert access_token is not None
    
    decoded_access_token = await service.decode_token(access_token)
    assert decoded_access_token is not None
    assert decoded_access_token.get("iss") == fixture.issuer
