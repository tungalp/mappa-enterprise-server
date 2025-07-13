import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from mapa.manage.organization_role.organization_role_model import CreateOrganizationRole, OrganizationRole
from mapa.manage.organization_role.organization_role_service import OrganizationRoleService
from .conftest import ManageFixture, tenant_id
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.role.role_model import CreateRole
from mapa.manage.role.role_service import RoleService
from mapa.manage.api.api_service import ApiService
from .data import generate_organization_role
from nanoid import generate
from mapa.manage.organization_client.organization_client_service import OrganizationClientService


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)  
    organization_client_service = OrganizationClientService(async_db)
  
    return {
        "organization_role_service": OrganizationRoleService(async_db),
        "organization_type_service": OrganizationTypeService(async_db),
        "organization_service": OrganizationService(async_db,organization_client_service),
        "role_service": RoleService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["organization_role_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["role_service"] is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["organization_role_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["role_service"] is not None

    organization_role_service: OrganizationRoleService = services["organization_role_service"]
    organization_type_service: OrganizationTypeService = services["organization_type_service"]
    organization_service: OrganizationService = services["organization_service"]
    role_service: RoleService = services["role_service"]
    
    assert organization_role_service is not None
    assert organization_type_service is not None
    assert organization_service is not None
    assert role_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await organization_role_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Organization Type eklenir.
    organizationTypeData = await organization_type_service.create(CreateOrganizationType(
        name="Test_organizationtype_name_role", description="Test_organizationtype_desc_role",is_root=False), str(tenant_id))
    assert organizationTypeData is not None
    
    # Organization eklenir.
    organizationData = await organization_service.create(CreateOrganization(is_root=False, organization_type_id=organizationTypeData.id,
        name="Test_organization_name_role", description="Test_organization_desc_role"), str(tenant_id))
    assert organizationData is not None
    
    # Role eklenir.
    roleData = await role_service.create(CreateRole(description="test",
        name=f"Test_role_organization_role"+generate(size=4)), str(tenant_id))
    assert roleData is not None
    
    create_organization_role: CreateOrganizationRole = generate_organization_role(roleData.id,organizationData.id)
    organization_role: OrganizationRole  = await organization_role_service.create(create_organization_role, str(tenant_id))
    assert organization_role is not None

    organization_role = await organization_role_service.get(organization_role.id)
    assert organization_role is not None

    is_deleted = await organization_role_service.delete(organization_role.id)
    assert is_deleted == True
    
    # Organization sorgulanır.
    query_OrganizationData1 = await organization_service.get(organizationData.id, tenant_id=str(tenant_id))
    assert query_OrganizationData1.id == organizationData.id

    # Organization silinir.
    deleted_OrganizationData = await organization_service.delete(organizationData.id)
    assert deleted_OrganizationData is not None

    # Organization Type sorgulanır.
    query_OrganizationTypeData1 = await organization_type_service.get(organizationTypeData.id, tenant_id=str(tenant_id))
    assert query_OrganizationTypeData1.id == organizationTypeData.id

    # Organization Type silinir.
    deleted_OrganizationTypeData = await organization_type_service.delete(organizationTypeData.id)
    assert deleted_OrganizationTypeData is not None
    
    # Role sorgulanır.
    query_roleData = await role_service.get(roleData.id, tenant_id=str(tenant_id))
    assert query_roleData.id == roleData.id

    # Role silinir.
    deleted_roleData = await role_service.delete(roleData.id)
    assert deleted_roleData is not None
    
