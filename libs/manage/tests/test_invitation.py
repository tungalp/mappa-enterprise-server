import asyncio
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.invitation.invitation_service import InvitationService
from mapa.manage.invitation.invitation_model import CreateInvitation,Invitation
from .conftest import ManageFixture, tenant_id
from uuid import uuid4
from .data import generate_invitation
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.user.user_model import CreateUser
from mapa.manage.user.user_service import UserService
from mapa.manage.api.api_service import ApiService
from typing import Any, Dict
from nanoid import generate


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db,organization_client_service)
    return {
        "invitation_service": InvitationService(async_db),
        "organization_type_service": OrganizationTypeService(async_db),
        "organization_service": organization_service,
        "user_service": UserService(async_db, api_service,organization_service),
    }

@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["invitation_service"] is not None
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["user_service"] is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """ApiService Crud Test"""
    services = await create_services(fixture)
    assert services["organization_type_service"] is not None
    assert services["organization_service"] is not None
    assert services["invitation_service"] is not None
    assert services["user_service"] is not None
    
    invitation_service: InvitationService = services["invitation_service"]
    organization_type_service: OrganizationTypeService = services["organization_type_service"]
    organization_service: OrganizationService = services["organization_service"]
    user_service: UserService = services["user_service"]
    
    assert organization_type_service is not None
    assert organization_service is not None
    assert invitation_service is not None
    assert user_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await invitation_service.get(uuid4(), tenant_id=str(tenant_id))
    assert empty_item is None

    # Organization Type eklenir.
    organizationTypeData = await organization_type_service.create(CreateOrganizationType(
        name="Test_organizationtype_name_invi", description="Test_organizationtype_desc_invi"), str(tenant_id))
    assert organizationTypeData is not None
    
    # Organization eklenir.
    organizationData = await organization_service.create(CreateOrganization(is_root=False, organization_type_id=organizationTypeData.id,
        name="Test_organization_name_invi", description="Test_organization_desc_invi"), str(tenant_id))
    assert organizationData is not None

    # User eklenir.
    userData = await user_service.create(CreateUser(
        name=f"Test_user_organization"+generate(size=4), surname="Test_user",
        email=f"test_organization_"+generate(size=4)+"@gmail.com", password="1123124",
        subject_id="112317723"+generate(size=4), phone="1"), str(tenant_id))
    assert userData is not None
    
    create_invitation: CreateInvitation = generate_invitation(userData.id,userData.email,organizationData.id)
    invitation: Invitation = await invitation_service.create(create_invitation, str(tenant_id))
    assert invitation is not None

    invitation = await invitation_service.get(invitation.id)
    assert invitation is not None

    is_deleted = await invitation_service.delete(invitation.id)
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
    
