
import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.base_layer.base_layer_model import (BaseLayer,
                                                     UpdateAllBaseLayer,
                                                     UpdateBaseLayer)
from mapa.spatial.base_layer.base_layer_service import BaseLayerService
from mapa.spatial.constant import BaseLayerTypes

from .conftest import SpatialFixture
from .data import generate_base_layer, tenant_id


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    return {
        "base_layer_service": BaseLayerService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    base_layer_service: BaseLayerService = services["base_layer_service"]

    assert base_layer_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """BaseLayerService Crud Test"""
    services = await create_services(fixture)
    base_layer_service: BaseLayerService = services["base_layer_service"]

    assert base_layer_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await base_layer_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (base_layer_service.create(generate_base_layer(), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await base_layer_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "type": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = BaseLayerTypes.WebMapTileService
    first_item: BaseLayer = items[0]

    updated_first_item = await base_layer_service.update(first_item.id, UpdateBaseLayer(
        type=test_value
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.type == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="type", op=FilterOp.LIKE, value=BaseLayerTypes.WebMapTileService+"%")
    ])
    test_value_2 = BaseLayerTypes.WebMapTileService
    updated_el_count = await base_layer_service.update_all(query_args_update, UpdateAllBaseLayer(
        type=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count > 0

    # ilk elemanı sorgulanır
    updated_first_item = await base_layer_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.type == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await base_layer_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await base_layer_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="type", op=FilterOp.LIKE, value=BaseLayerTypes.WebMapService+"%")
    ])
    deleted_row_count = await base_layer_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await base_layer_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
