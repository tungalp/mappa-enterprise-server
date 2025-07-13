import pytest
from urllib import parse
from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.manage.client.client_service import ClientService
from .conftest import SsoFixture
from ..data import client_manage, client_id_manage


async def create_service(fixture: SsoFixture) -> AuthUtilService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)

    return AuthUtilService(
        fixture.jwt_secret,
    )


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""

    service: AuthUtilService = await create_service(fixture)
    assert service is not None


@pytest.mark.asyncio
async def test_code_challange(fixture: SsoFixture):
    """Service"""

    service: AuthUtilService = await create_service(fixture)
    code_verifier = service.generate_code_verifier()
    code_challenge = service.generate_code_challenge(code_verifier)

    assert code_verifier and code_challenge

