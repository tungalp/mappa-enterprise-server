import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.manage.constants import ApplicationTypes
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from mapa.manage.organization_client.organization_client_model import CreateOrganizationClient, OrganizationClient
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from .conftest import ManageFixture
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.client.client_model import CreateClient
from mapa.manage.client.client_service import ClientService
from mapa.manage.api.api_service import ApiService
from mapa.manage.tenant_client.tenant_client_service import TenantClientService
from .data import generate_organization_client
from nanoid import generate

async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    tenant_client_service = TenantClientService(async_db)
    organization_client_service = OrganizationClientService(async_db)
    organization_service =  OrganizationService(async_db,organization_client_service)
    api_scope_service = ApiScopeService(async_db)
    return {
        "organization_client_service": organization_client_service,
        "organization_type_service": OrganizationTypeService(async_db),
        "organization_service": organization_service,
        "client_service": ClientService(async_db,tenant_client_service,api_scope_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["organization_client_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["client_service"] is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["organization_client_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["client_service"] is not None

    organization_client_service: OrganizationClientService = services["organization_client_service"]
    organization_type_service: OrganizationTypeService = services["organization_type_service"]
    organization_service: OrganizationService = services["organization_service"]
    client_service: ClientService = services["client_service"]
    
    assert organization_client_service is not None
    assert organization_type_service is not None
    assert organization_service is not None
    assert client_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await organization_client_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Organization Type eklenir.
    organizationTypeData = await organization_type_service.create(CreateOrganizationType(
        name="Test_organizationtype_name_client", description="Test_organizationtype_desc_client",is_root=False), str(fixture.tenant_id))
    assert organizationTypeData is not None
    
    # Organization eklenir.
    organizationData = await organization_service.create(CreateOrganization(is_root=False, organization_type_id=organizationTypeData.id,
        name="Test_organization_name_client", description="Test_organization_desc_client"), str(fixture.tenant_id))
    assert organizationData is not None
    
    # Client eklenir.
    clientData = await client_service.create(CreateClient(
        name="client_test_organization"+generate(size=4),
        grant_types=["authorization_code"],
        application_type=ApplicationTypes.WEB,
        logo_url="https://www.mapa.com.tr/application/views/islemgis/layouts/images/logo-colored.png"), str(fixture.tenant_id))
    assert clientData is not None
    
    create_organization_client: CreateOrganizationClient = generate_organization_client(clientData.client_id,organizationData.id)
    organization_client: OrganizationClient  = await organization_client_service.create(create_organization_client, str(fixture.tenant_id))
    assert organization_client is not None

    organization_client = await organization_client_service.get(organization_client.id)
    assert organization_client is not None

    is_deleted = await organization_client_service.delete(organization_client.id)
    assert is_deleted == True
    
    # Organization sorgulanır.
    query_OrganizationData1 = await organization_service.get(organizationData.id, tenant_id=str(fixture.tenant_id))
    assert query_OrganizationData1.id == organizationData.id

    # Organization silinir.
    deleted_OrganizationData = await organization_service.delete(organizationData.id)
    assert deleted_OrganizationData is not None

    # Organization Type sorgulanır.
    query_OrganizationTypeData1 = await organization_type_service.get(organizationTypeData.id, tenant_id=str(fixture.tenant_id))
    assert query_OrganizationTypeData1.id == organizationTypeData.id

    # Organization Type silinir.
    deleted_OrganizationTypeData = await organization_type_service.delete(organizationTypeData.id)
    assert deleted_OrganizationTypeData is not None
    
    # Client sorgulanır.
    query_clientData = await client_service.get(clientData.id, tenant_id=str(fixture.tenant_id))
    assert query_clientData is not None
    assert query_clientData.id == clientData.id

    # Client silinir.
    deleted_clientData = await client_service.delete(clientData.id)
    assert deleted_clientData is not None
    
