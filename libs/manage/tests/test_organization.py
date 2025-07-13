import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_model import CreateOrganization, Organization, UpdateAllOrganization, UpdateOrganization
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType, OrganizationType, UpdateAllOrganizationType, UpdateOrganizationType
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.organization_user.organization_user_service import OrganizationUserService
from .conftest import ManageFixture
from uuid import UUID, uuid4
import uuid
from .data import generate_organization,generate_organization_child,generate_organization_client,generate_organization_user,user_id
from nanoid import generate

async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    organization_client_service = OrganizationClientService(async_db)
    organization_user_service = OrganizationUserService(async_db)
    return {
        "organization_type_service": OrganizationTypeService(async_db),
        "organization_client_service": organization_client_service,
        "organization_user_service": organization_user_service,
        "organization_service": OrganizationService(async_db,organization_client_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["organization_client_service"] is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["organization_client_service"] is not None

    organization_type_service: OrganizationTypeService = services["organization_type_service"]
    organization_service: OrganizationService = services["organization_service"]
    organization_client_service: OrganizationClientService = services["organization_client_service"]

    assert organization_type_service is not None
    assert organization_service is not None
    assert organization_client_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await organization_service.get(uuid4(), tenant_id=str(fixture.tenant_id))
    assert empty_item is None
    
    # Organization Type eklenir.
    organizationTypeData = await organization_type_service.create(CreateOrganizationType(
        name="Test_organizationtype_name_Test", description="Test_organizationtype_desc_Test",is_root=False), str(fixture.tenant_id))
    assert organizationTypeData is not None

    # Yeni test kayıdı oluşturulur
    organizationData = await organization_service.create(generate_organization(organizationTypeData.id), tenant_id=str(fixture.tenant_id))
    assert organizationData is not None

    # Id listesine göre kayıtları getir
    selected_items = await organization_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in [organizationData]])
    ], order={
        "name": "desc"
    }), tenant_id=str(fixture.tenant_id))
    assert len(selected_items) == 1

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Organization = organizationData

    updated_first_item = await organization_service.update(first_item.id, UpdateOrganization(
        name=test_value
    ), tenant_id=str(fixture.tenant_id))
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik_test"
    updated_el_count = await organization_service.update_all(query_args_update, UpdateAllOrganization(
        description=test_value_2
    ), tenant_id=str(fixture.tenant_id))
    assert updated_el_count > 0

    # ilk elemanı sorgulanır
    updated_first_item = await organization_service.get(first_item.id, tenant_id=str(fixture.tenant_id))
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await organization_service.delete(updated_first_item.id, str(fixture.tenant_id))
    assert first_row_deleted is True

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])

    # Silinenler sorgulanır
    deleted_rows = await organization_service.find(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert len(deleted_rows) == 0

    # Organization Type sorgulanır.
    query_OrganizationTypeData1 = await organization_type_service.get(organizationTypeData.id, tenant_id=str(fixture.tenant_id))
    assert query_OrganizationTypeData1.id == organizationTypeData.id

    # Organization Type silinir.
    deleted_OrganizationTypeData = await organization_type_service.delete(organizationTypeData.id)
    assert deleted_OrganizationTypeData is not None
    
    
@pytest.mark.asyncio
async def test_get_hierarchical_organization_by_client_id(fixture: ManageFixture):
    
    test_manage_id = "client_id_manage"
    
    """Service"""
    services = await create_services(fixture)
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["organization_client_service"] is not None
    assert services["organization_user_service"] is not None

    organization_type_service: OrganizationTypeService = services["organization_type_service"]
    organization_service: OrganizationService = services["organization_service"]
    organization_client_service: OrganizationClientService = services["organization_client_service"]
    organization_user_service: OrganizationUserService = services["organization_user_service"]

    assert organization_type_service is not None
    assert organization_service is not None
    assert organization_client_service is not None
    assert organization_user_service is not None
    
    # Organization Type eklenir.
    organizationTypeData = await organization_type_service.create(CreateOrganizationType(
        name="Test_organizationtype_name_Test_hierarchical", description="Test_organizationtype_desc_Test_hierarchical",is_root=False), str(fixture.tenant_id))
    assert organizationTypeData is not None
    
    # Root Organization test kayıdı oluşturulur
    organizationData_root = await organization_service.create(generate_organization(organizationTypeData.id), tenant_id=str(fixture.tenant_id))
    assert organizationData_root is not None
    
    # Child_1 Organization test kayıdı oluşturulur
    organizationData_child_1 = await organization_service.create(generate_organization_child(organizationTypeData.id,organizationData_root.id), tenant_id=str(fixture.tenant_id))
    assert organizationData_child_1 is not None
    
    # Child_2 Organization test kayıdı oluşturulur
    organizationData_child_2 = await organization_service.create(generate_organization_child(organizationTypeData.id,organizationData_child_1.id), tenant_id=str(fixture.tenant_id))
    assert organizationData_child_2 is not None
    
    # Organization Client test kayıdı oluşturulur
    organization_client = await organization_client_service.create(generate_organization_client(test_manage_id,organizationData_root.id,True), tenant_id=str(fixture.tenant_id))
    assert organization_client is not None
    
    # Organization User test kayıdı oluşturulur (user'ı organization'a bağla)
    organization_user = await organization_user_service.create(generate_organization_user(user_id,organizationData_root.id), tenant_id=str(fixture.tenant_id))
    assert organization_user is not None
    
    empty_hierarchical_datas = await organization_service.get_hierarchical_organization_by_client_id(str(uuid4()),str(user_id), tenant_id=str(fixture.tenant_id))
    assert len(empty_hierarchical_datas) == 0
    
    hierarchical_datas = await organization_service.get_hierarchical_organization_by_client_id(str(test_manage_id), str(user_id),tenant_id=str(fixture.tenant_id))
    assert len(hierarchical_datas) > 0
    
    # Test Dataları Silinir
    # Not : Apps tarafında da test etmek için silme işlemleri kapatılabilir.
    c = await organization_client_service.delete_by_ids([organization_client.id], tenant_id=str(fixture.tenant_id))
    assert c == 1
    
    o = await organization_service.delete_by_ids([organizationData_root.id], tenant_id=str(fixture.tenant_id))
    assert o == 3
    
    ot = await organization_type_service.delete_by_ids([organizationTypeData.id], tenant_id=str(fixture.tenant_id))
    assert ot == 1