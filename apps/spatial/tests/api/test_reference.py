import asyncio
from typing import Any, Dict, List
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.reference.reference_model import (CreateReference, Reference,
                                                   UpdateReference)
from mapa.spatial.reference.reference_service import ReferenceService

from .conftest import SpatialFixture
from .data import generate_reference, tenant_id


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    return {
        "reference_service": ReferenceService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    reference_service: ReferenceService = services["reference_service"]

    assert reference_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """ReferenceService Crud Test"""
    services = await create_services(fixture)
    reference_service: ReferenceService = services["reference_service"]

    assert reference_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await reference_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni test kayıtları oluşturulur
    lst: List[CreateReference] = generate_reference()
    el_count = len(lst)
    task_list = (reference_service.create(lst[i], tenant_id=tenant_id)
                 for i in range(0, el_count))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Reference = items[0]

    updated_first_item = await reference_service.update(first_item.id, UpdateReference(
        epsgcode=first_item.epsgcode, wkt=first_item.wkt,  wkid=test_value, projcs=first_item.projcs,name=first_item.name
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.wkid == test_value

    # ilk elemanı sorgulanır
    updated_first_item = await reference_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.wkid == test_value

    # ilk kayıt silinir
    first_row_deleted = await reference_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await reference_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="wkid", op=FilterOp.NOT_NULL, value=test_value)
    ])
    deleted_row_count = await reference_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await reference_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
