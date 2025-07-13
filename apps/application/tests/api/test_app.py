import asyncio
from typing import Any, Dict
import pytest
from unittest.mock import AsyncMock
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.application.app.app_model import App, CreateApp, UpdateAllApp, UpdateApp
from mapa.application.app.app_service import AppService
from mapa.application.content_page.content_page_service import ContentPageService
from .conftest import ApplicationFixture, ManageFixture
from ..data import tenant_id, generate_app
from uuid import uuid4


async def create_services(fixture: ApplicationFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)

    fixture_manage = ManageFixture()
    initialized_manage = await fixture_manage.create_test_data()
    assert initialized_manage is True
    async_db_manage = fixture_manage.create_db_instance(
        fixture_manage.db_url_async)

    content_page_service = ContentPageService(async_db)
    
    # Create mock messenger for testing
    mock_messenger = AsyncMock()
    mock_client_id = uuid4()
    mock_api_id = uuid4()
    mock_client_api_id = uuid4()
    
    mock_messenger.get_client_by_client_id.return_value = {"id": mock_client_id}
    mock_messenger.get_api.return_value = {"id": mock_api_id}
    mock_messenger.create_client.return_value = {"id": mock_client_id, "client_id": "test_client_id", "client_secret": "test_secret"}
    mock_messenger.create_api.return_value = {"id": mock_api_id}
    mock_messenger.create_client_api.return_value = {"id": mock_client_api_id}
    mock_messenger.create_api_scopes.return_value = True
    mock_messenger.delete_client_api.return_value = True
    mock_messenger.delete_api.return_value = True
    mock_messenger.delete_client.return_value = True
    mock_messenger.delete_all_clients.return_value = True
    
    app_service = AppService(async_db_manage, content_page_service, mock_messenger)
    
    return {
        "ContentPageService": content_page_service,
        "AppService": app_service
    }


@pytest.mark.asyncio
async def test_create_services(fixture: ApplicationFixture):
    """Service"""
    services = await create_services(fixture)

    app_service: AppService = services["AppService"]
    content_page_service: ContentPageService = services["ContentPageService"]

    assert app_service is not None
    assert content_page_service is not None


@pytest.mark.asyncio
async def test_create_data(fixture: ApplicationFixture):
    """AppService Create Test"""
    services = await create_services(fixture)
    service: AppService = services["AppService"]
    assert service is not None

    create_app: CreateApp = generate_app()
    app: App = await service.create(create_app, tenant_id)
    assert app is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ApplicationFixture):
    """AppService Crud Test"""
    services = await create_services(fixture)
    service: AppService = services["AppService"]
    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get(uuid4(), tenant_id=fixture.tenant_id)
    assert empty_item is None

    create_app: CreateApp = generate_app()
    app = await service.create(create_app, fixture.tenant_id)
    assert app is not None

    app = await service.get(app.id, fixture.tenant_id)
    assert app is not None

    isDeleted = await service.delete(app.id, fixture.tenant_id)
    assert isDeleted == True


@pytest.mark.asyncio
async def test_query(fixture: ApplicationFixture):
    """AppService Crud Test"""
    services = await create_services(fixture)
    service: AppService = services["AppService"]

    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get(uuid4(), tenant_id=fixture.tenant_id)
    assert empty_item is None

    queryArgs = QueryArgs(where=[], offset=0, limit=0)
    # Id listesine göre kayıtları getir
    selected_items = await service.find(queryArgs, tenant_id=fixture.tenant_id)
    # Id listesine göre kayıtları siler
    deleted_count = await service.delete_all(queryArgs, tenant_id=fixture.tenant_id)
    assert len(selected_items) == deleted_count
