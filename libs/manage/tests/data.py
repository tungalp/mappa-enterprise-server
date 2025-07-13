import uuid
from bcrypt import gensalt, hashpw
from mapa.manage.api.api_entity import ApiEntity
from mapa.manage.api_scope.api_scope_entity import ApiScopeEntity
from mapa.manage.client.client_entity import ClientEntity
from mapa.manage.client_api.client_api_entity import ClientApiEntity
from mapa.manage.client_api_scope.client_api_scope_entity import ClientApiScopeEntity
from mapa.manage.constants import LevelTypes
from mapa.manage.invitation.invitation_model import CreateInvitation
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.organization_client.organization_client_model import CreateOrganizationClient
from mapa.manage.organization_role.organization_role_model import CreateOrganizationRole
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser
from mapa.manage.profile_adaptor.profile_adaptor_entity import ProfileAdaptorEntity
from mapa.manage.role.role_entity import RoleEntity
from mapa.manage.role_api_scope.role_api_scope_entity import RoleApiScopeEntity
from mapa.manage.role_user.role_user_entity import RoleUserEntity
from mapa.manage.tenant.tenant_entity import TenantEntity
from mapa.manage.tenant_client.tenant_client_entity import TenantClientEntity
from mapa.manage.tenant_user.tenant_user_entity import TenantUserEntity
from mapa.manage.user.user_entity import UserEntity
from nanoid import generate
from uuid import UUID, uuid4
from datetime import datetime, timedelta

session_id = uuid.UUID("e7966430-19c8-4e70-acdd-8737ff67cce9")

user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")
user = UserEntity(
    id=user_id,
    name="admin",
    surname="admin",
    email="admin@admin.com",
    password=hashpw("admin".encode("utf-8"), gensalt()).decode("utf-8")
)

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
tenant = TenantEntity(
    id=tenant_id,
    name="Admin",
    title="Admin Tenant",
    user_id=user_id
)
tenant_user = TenantUserEntity(
    user_id=user_id,
    tenant_id=tenant_id,
    role="owner"
)

user_2_id = uuid.UUID("2d943171-9c9e-4c95-806a-566bd725a436")
user2 = UserEntity(
    id=user_2_id,
    name="member",
    surname="member",
    email="member@member.com",
    password=hashpw("member".encode("utf-8"), gensalt()).decode("utf-8")
)

tenant_2_id = uuid.UUID("85e94027-6edd-4053-b518-8a195f10edbf")
tenant2 = TenantEntity(
    id=tenant_2_id,
    name="Member",
    title="Member Tenant",
    user_id=user_2_id
)
tenant_2_user = TenantUserEntity(
    user_id=user_2_id,
    tenant_id=tenant_2_id,
    role="owner"
)

client_id_manage = uuid.UUID("fa2518dd-5b27-4a59-b740-e96c3c79160a")
client_manage = ClientEntity(
    id=client_id_manage,
    name="manage",
    client_id="client_id_manage",
    client_secret="client_secret_manage",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:33001/callback"],
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_manage = TenantClientEntity(
    client_id=client_id_manage,
    tenant_id=tenant_id
)

client_id_workspace = uuid.UUID("891981ea-85ba-40bb-b150-409e339e5b65")
client_workspace = ClientEntity(
    id=client_id_workspace,
    name="workspace",
    client_id="client_id_workspace",
    client_secret="client_secret_workspace",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:33002/callback"],
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_workspace = TenantClientEntity(
    client_id=client_id_workspace,
    tenant_id=tenant_id
)


client_id_gateway = uuid.UUID("858b742b-29d1-469d-87d7-9095ef0fcbf0")
client_gateway = ClientEntity(
    id=client_id_gateway,
    name="gateway",
    client_id="client_id_gateway",
    client_secret="client_secret_gateway",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:33003/callback"],
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_gateway = TenantClientEntity(
    client_id=client_id_gateway,
    tenant_id=tenant_id
)

client_id_application = uuid.UUID("111981ea-85ba-40bb-b150-150e339e5b65")
client_application = ClientEntity(
    id=client_id_application,
    name="application",
    client_id="client_id_application",
    client_secret="client_secret_application",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:33003/callback"],
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_application = TenantClientEntity(
    client_id=client_id_application,
    tenant_id=tenant_id
)

client_id_test = uuid.UUID("d858b93d-5b5b-49b6-8302-9f96be0ea36a")
client_test = ClientEntity(
    id=client_id_test,
    name="test",
    client_id="client_id_test",
    client_secret="client_secret_test",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:3000"],
    is_system=False,
    level_type= LevelTypes.THIRD_PARTY,
    require_pkce=False
)
tenant_client_test = TenantClientEntity(
    client_id=client_id_test,
    tenant_id=tenant_id
)

client_id_test_2 = uuid.UUID("7c17eed3-e345-4d83-875c-d1a053a436b9")
client_test_2 = ClientEntity(
    id=client_id_test_2,
    name="test2",
    client_id="client_id_test_2",
    client_secret="client_secret_test_2",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:3000"],
    is_system=False,
    level_type= LevelTypes.THIRD_PARTY,
    require_pkce=False
)
tenant_client_test_2 = TenantClientEntity(
    client_id=client_id_test_2,
    tenant_id=tenant_2_id
)


nonce = "B6XMlQUsILYjf7oK9ElT1"
audience = "https://test-server/api/v1"

instances = [
    user, tenant, tenant_user, user2, tenant2, tenant_2_user,
    client_manage, tenant_client_manage,
    client_workspace, tenant_client_workspace,
    client_gateway, tenant_client_gateway,    
    client_application, tenant_client_application, 
    client_test, tenant_client_test,
    client_test_2, tenant_client_test_2
    ]


role_by_user_field_list = [
    "id",
    "name",
    "description",
    "users.id",
    "users.name",
    "users.surname",
    "users.email",
    "users.password",
    "users.email_verified",
    "users.phone",
    "users.subject_id",
    "users.context",
    "users.created_at",
]

role_by_api_scope_field_list = [
    "id",
    "name",
    "description",
    "api_scopes.id",
    "api_scopes.name",
    "api_scopes.description",
    "api_scopes.api_id"
]

user_by_role_field_list = [
    "id",
    "name",
    "surname",
    "email",
    "password",
    "email_verified",
    "phone",
    "subject_id",
    "context",
    "created_at",
    "roles.id",
    "roles.name",
    "roles.description",
]

client_api_field_list = [
    "id",
    "client_id",
    "api_id",
    "api_scopes.id",
    "api_scopes.name",
    "api_scopes.description",
    "api_scopes.api_id"
]

api_scope_role_field_list = [
    "id",
    "role_id",
    "api_scope_id",
    "role.id",
    "role.name",
    "role.description",
    "api_scope.id",   
    "api_scope.name",
    "api_scope.description",
]


role_user_field_list = [
    "id",
    "role_id",
    "user_id",
    "expired_at",
    "user.id",
    "user.name",
    "user.surname",
    "user.email",
    "user.password",
    "user.email_verified",
    "user.phone",
    "user.subject_id",
    "user.context",
    "user.created_at",
    "role.id",
    "role.name",
    "role.description",
]

def generate_organization_type() -> CreateOrganizationType:
    return CreateOrganizationType(
        name="organization_type_test"+generate(size=4),
        description="Test"+generate(size=4),
        is_root=False) 

def generate_organization(organization_type_id: UUID = uuid4()) -> CreateOrganization:
    return CreateOrganization(
        name="organiza_test_"+generate(size=4),
        description="Test"+generate(size=4),
        is_root=False,
        organization_type_id=organization_type_id)
     
def generate_organization_child(organization_type_id: UUID = uuid4(), parent_id: UUID = uuid4()) -> CreateOrganization:
    return CreateOrganization(
        name="organiza_test_"+generate(size=4),
        description="Test"+generate(size=4),
        is_root=False,
        organization_type_id=organization_type_id,
        parent_id=parent_id) 
    
def generate_invitation(user_id: UUID = uuid4(),user_email=generate(size=4),organization_id: UUID = uuid4()) -> CreateInvitation:
    return CreateInvitation(
        organization_id=organization_id,
        user_id=user_id, 
        tenant=tenant_id, 
        expired_at=datetime.now(),
        email=user_email)

def generate_organization_user(user_id: UUID = uuid4(),organization_id: UUID = uuid4()) -> CreateOrganizationUser:
    return CreateOrganizationUser(
        organization_id=organization_id,
        user_id=user_id)
    
def generate_organization_role(role_id: UUID = uuid4(),organization_id: UUID = uuid4()) -> CreateOrganizationRole:
    return CreateOrganizationRole(
        organization_id=organization_id,
        role_id=role_id)
    
def generate_organization_client(client_id: str,organization_id: UUID = uuid4(),is_hierarchical:bool=False) -> CreateOrganizationClient:
    return CreateOrganizationClient(
        organization_id=organization_id,
        client_id=client_id,
        is_hierarchical=is_hierarchical)