import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.definition.definition_model import (Definition,
                                                     UpdateAllDefinition,
                                                     UpdateDefinition)
from mapa.spatial.definition.definition_service import DefinitionService

from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService
    
from .conftest import SpatialFixture
from .data import generate_definition, tenant_id


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)


    layer_definition_service= LayerDefinitionService(async_db)
    layer_hook_service= LayerHookService(async_db)
    return {
        "definition_service": DefinitionService(async_db,layer_definition_service,layer_hook_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    definition_service: DefinitionService = services["definition_service"]

    assert definition_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """DefinitionService Crud Test"""
    services = await create_services(fixture)
    definition_service: DefinitionService = services["definition_service"]

    assert definition_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await definition_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (definition_service.create(generate_definition(), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await definition_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "title": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Definition = items[0]

    updated_first_item = await definition_service.update(first_item.id, UpdateDefinition(
        is_attribute_panel=first_item.is_attribute_panel,
        organization_geo_constraint=first_item.organization_geo_constraint,
        is_base_layer=first_item.is_base_layer,
        title=test_value,
        default_extent=first_item.default_extent,
        max_scale=first_item.max_scale,
        min_scale=first_item.min_scale,
        opacity=first_item.opacity,
        timer=first_item.timer,
        field_params=first_item.field_params,
        style_params=first_item.style_params,
        topology_rules_params=first_item.topology_rules_params,
        filter_params=first_item.filter_params,
        edit_snap_scale=first_item.edit_snap_scale,
        data_type=first_item.data_type,
        key_field=first_item.key_field,
        target_namespace=first_item.target_namespace,
        type_name=first_item.type_name,
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.title == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="title", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await definition_service.update_all(query_args_update, UpdateAllDefinition(
        title=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await definition_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.title == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await definition_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await definition_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="title", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await definition_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await definition_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
