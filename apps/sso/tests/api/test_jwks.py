from datetime import datetime, timedelta
import pytest

from mapa.sso.jwk.jwk_service import JwkService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> JwkService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    jwks_service = JwkService(async_db)
    return jwks_service


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    service: JwkService = await create_service(fixture)

    assert service is not None
    
    
@pytest.mark.asyncio
async def test_create_jwks(fixture: SsoFixture):
    """Service"""
    service: JwkService = await create_service(fixture)
    assert service is not None
    
    expired_at = datetime.now() + timedelta(days=30)
    jwk = await service.create_jwk(expired_at)
    assert jwk is not None
    
@pytest.mark.asyncio
async def test_get_active_set(fixture: SsoFixture):
    """Service"""
    service: JwkService = await create_service(fixture)
    assert service is not None
    
    jwk_list = await service.get_active_set(limit=2)
    assert jwk_list is not None
    assert len(jwk_list) == 2
