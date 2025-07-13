import asyncio
from uuid import UUID
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.consent.consent_model import CreateConsent, UpdateConsent
from mapa.sso.consent.consent_service import ConsentService
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser
from mapa.manage.user.user_service import UserService
from .conftest import SsoFixture
from ..data import client_manage


async def create_service(fixture: SsoFixture) -> ConsentService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    return ConsentService(async_db)


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    service: ConsentService = await create_service(fixture)

    assert service is not None

@pytest.mark.asyncio
async def test_crud_consent(fixture: SsoFixture):
    """Service"""

    service: ConsentService = await create_service(fixture)
    assert service is not None
    
    # Boş bir sorgulama yapılır
    empty_item = await service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84")
    assert empty_item is None
    
    # Kullanıcı id
    user_id = "7175e67d-0ddc-4c96-a167-c3f3ef72de5a"
    
    item = await service.create(CreateConsent(
        user_id=UUID(user_id),
        client_id=client_manage.id,
        scopes=["openid", "profile", "email", "offline_access"],
        accepted=True))
    assert item is not None
    
    # İtem veritabanından geri getirilir
    selected_item = await service.find_one(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[str(item.id)])
    ]))
    assert item.id == selected_item.id
    
    # ilk elemanın bir özniteliği değiştirilir
    test_value = ["openid", "profile", "email", "test"]

    updated_first_item = await service.update(item.id, UpdateConsent(
        scopes=test_value,
        accepted=False
    ))
    assert updated_first_item.scopes == test_value
    assert updated_first_item.updated_at is not None
    assert updated_first_item.accepted is False

    # ilk kayıt silinir
    first_row_deleted = await service.delete(updated_first_item.id)
    assert first_row_deleted is True

    # Silinenler sorgulanır
    deleted_item = await service.get(item.id)
    assert deleted_item is None
