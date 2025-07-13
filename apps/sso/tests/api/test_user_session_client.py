import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import uuid4
import uuid
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.user.user_model import CreateUser
from mapa.manage.user.user_service import UserService
from mapa.sso.user_session.user_session_model import CreateUserSession, UpdateAllUserSession, UpdateUserSession
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.user_session_client.user_session_client_model import CreateUserSessionClient, UpdateUserSessionClient
from mapa.sso.user_session_client.user_session_client_service import UserSessionClientService
from .conftest import SsoFixture
from ..data import user as default_user
from mapa.manage.api.api_service import ApiService


async def create_services(fixture: SsoFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db,organization_client_service)
    return {
        "user_session": UserSessionService(async_db),
        "user": UserService(async_db, api_service,organization_service),
        "user_session_client": UserSessionClientService(async_db)
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    services = await create_services(fixture)

    assert services["user_session_client"] is not None
    assert services["user_session"] is not None
    assert services["user"] is not None


@pytest.mark.asyncio
async def test_crud_user_session_client(fixture: SsoFixture):
    """Service"""
    services = await create_services(fixture)

    assert services["user_session_client"] is not None
    assert services["user_session"] is not None
    assert services["user"] is not None

    service: UserSessionService = services["user_session"]
    user_service: UserService = services["user"]
    session_client_service: UserSessionClientService = services["user_session_client"]

    user = await user_service.create(CreateUser(name="test", surname="test", email="test@test.com.com"+str(uuid4()), password="123", phone="123"))
    user_session = await service.create(CreateUserSession(
        id=uuid4(),
        user_id=user.id,  # type: ignore
        authenticated_at=datetime.now(),
        authenticated=True,
        expired_at=datetime.now() + timedelta(minutes=10080)))

    user_sesssion_client = await session_client_service.create(CreateUserSessionClient(
        user_session_id=user_session.id,
        client_id=uuid.UUID(str(fixture.client_manage.id)),
        tenant=fixture.tenant_id,
        created_at=datetime.now()
    ))

    assert user_sesssion_client is not None

    tenant = uuid4()
    updated_item = await session_client_service.update(user_sesssion_client.id, UpdateUserSessionClient(
        tenant=tenant
    ))
    assert updated_item is not None
    assert updated_item.tenant == tenant
