import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser, OrganizationUser
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.organization_user.organization_user_service import OrganizationUserService
from .conftest import ManageFixture, tenant_id
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.user.user_model import CreateUser
from mapa.manage.user.user_service import UserService
from mapa.manage.api.api_service import ApiService
from .data import generate_organization_user
from nanoid import generate

async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    organization_client_service =  OrganizationClientService(async_db)
    organization_service =  OrganizationService(async_db,organization_client_service)
        
    return {
        "organization_user_service": OrganizationUserService(async_db),
        "organization_type_service": OrganizationTypeService(async_db),
        "organization_service": organization_service,
        "user_service": UserService(async_db, api_service,organization_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["organization_user_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["user_service"] is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["organization_user_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["user_service"] is not None

    organization_user_service: OrganizationUserService = services["organization_user_service"]
    organization_type_service: OrganizationTypeService = services["organization_type_service"]
    organization_service: OrganizationService = services["organization_service"]
    user_service: UserService = services["user_service"]
    
    assert organization_user_service is not None
    assert organization_type_service is not None
    assert organization_service is not None
    assert user_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await organization_user_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Organization Type eklenir.
    organizationTypeData = await organization_type_service.create(CreateOrganizationType(
        name="Test_organizationtype_name_user", description="Test_organizationtype_desc_user",is_root=False), str(tenant_id))
    assert organizationTypeData is not None
    
    # Organization eklenir.
    organizationData = await organization_service.create(CreateOrganization(is_root=False, organization_type_id=organizationTypeData.id,
        name="Test_organization_name_user", description="Test_organization_desc_user"), str(tenant_id))
    assert organizationData is not None
    
    # User eklenir.
    userData = await user_service.create(CreateUser(
        name=f"Test_user_organization"+generate(size=4), surname="Test_user",
        email=f"test_organization_"+generate(size=4)+"@gmail.com", password="1123124",
        subject_id="112317723"+generate(size=4), phone="1"), str(tenant_id))
    assert userData is not None
    
    create_organization_user: CreateOrganizationUser = generate_organization_user(userData.id,organizationData.id)
    organization_user: OrganizationUser  = await organization_user_service.create(create_organization_user, str(tenant_id))
    assert organization_user is not None

    organization_user = await organization_user_service.get(organization_user.id)
    assert organization_user is not None

    is_deleted = await organization_user_service.delete(organization_user.id)
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
    
    # User sorgulanır.
    query_userData = await user_service.get(userData.id, tenant_id=str(tenant_id))
    assert query_userData.id == userData.id

    # User silinir.
    deleted_userData = await user_service.delete(userData.id)
    assert deleted_userData is not None
    
