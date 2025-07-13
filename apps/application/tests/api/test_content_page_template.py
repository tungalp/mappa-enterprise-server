import asyncio
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import QueryArgs
from mapa.application.content_page_template.content_page_template_model import CreateContentPageTemplate
from mapa.application.content_page_template.content_page_template_service import ContentPageTemplateService
from .conftest import ApplicationFixture
from ..data import tenant_id, generate_app, generate_content_page_template
from uuid import uuid4
from typing import Any, Dict

async def create_services(fixture: ApplicationFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    return {
        "ContentPageTemplateService": ContentPageTemplateService(async_db)
    }


@pytest.mark.asyncio
async def test_create_services(fixture: ApplicationFixture):
    services = await create_services(fixture)
    content_page_service: ContentPageTemplateService = services["ContentPageTemplateService"]
    assert content_page_service is not None


@pytest.mark.asyncio
async def test_create_data(fixture: ApplicationFixture):
    """AppService Create Test"""
    services = await create_services(fixture)
    content_page_template_service: ContentPageTemplateService = services[
        "ContentPageTemplateService"]

    assert content_page_template_service is not None

    create_content_page: CreateContentPageTemplate = generate_content_page_template()
    content_page = await content_page_template_service.create(create_content_page, fixture.tenant_id)
    assert content_page is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ApplicationFixture):
    """AppService Crud Test"""
    services = await create_services(fixture)
    content_page_template_service: ContentPageTemplateService = services[
        "ContentPageTemplateService"]

    assert content_page_template_service is not None

    create_content_page: CreateContentPageTemplate = generate_content_page_template()
    content_page = await content_page_template_service.create(create_content_page, fixture.tenant_id)
    assert content_page is not None


@pytest.mark.asyncio
async def test_query(fixture: ApplicationFixture):
    """AppService Crud Test"""
    services = await create_services(fixture)
    content_page_service: ContentPageTemplateService = services["ContentPageTemplateService"]

    assert content_page_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await content_page_service.get(uuid4(), tenant_id=fixture.tenant_id)
    assert empty_item is None

    queryArgs = QueryArgs()

    # Id listesine göre kayıtları getir
    selected_items = await content_page_service.find(queryArgs, tenant_id=fixture.tenant_id)

    # Id listesine göre kayıtları siler
    deleted_count = await content_page_service.delete_all(queryArgs, tenant_id=fixture.tenant_id)
    assert len(selected_items) == deleted_count
