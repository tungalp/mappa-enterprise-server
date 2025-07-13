import os
import pathlib
from dependency_injector import containers
from dependency_injector import providers
from mapa.core.data import AsyncDatabase
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.manage.invitation.invitation_util_service import InvitationUtilService
from mapa.manage.messaging.consumer.api_consumers import (
    ApiCreateConsumer,
    ApiDeleteConsumer,
    ApiGetConsumer,
    ApiDeleteAllConsumer,
    ApiFindConsumer,
    ApiPagingConsumer,
    ApiCountConsumer,
    ApiUpdateConsumer,
)
from mapa.manage.messaging.consumer.client_consumers import (
    ClientCreateConsumer,
    ClientDeleteConsumer,
    ClientGetByClientIdConsumer,
    ClientDeleteAllConsumer,
    ClientFindConsumer,
    ClientPagingConsumer,
    ClientUpdateConsumer,
    ClientGetInfoConsumer,
    ClientGetConsumer,
    ClientGetScopesConsumer,
)
from mapa.manage.messaging.consumer.api_scope_consumers import (
    ApiScopeCreateAllConsumer,
    ApiScopeCreateConsumer,
    ApiScopeDeleteAllConsumer,
    ApiScopeFindConsumer,
    ApiScopePagingConsumer,
)

from mapa.manage.messaging.consumer.invitation_consumers import (
    InvitationGetConsumer,
    InvitationUpdateConsumer,
)

from mapa.manage.messaging.consumer.organization_consumers import (
    OrganizationCreateConsumer,
    OrganizationDeleteConsumer,
)

from mapa.manage.messaging.consumer.organization_user_consumers import (
    OrganizationUserCreateConsumer,
    OrganizationUserDeleteConsumer,
)

from mapa.manage.messaging.consumer.organization_type_consumers import (
    OrganizationTypeCreateConsumer,
    OrganizationTypeDeleteConsumer,
)
from mapa.manage.messaging.consumer.tenant_user_consumers import (
    TenantUserFindByUserIdConsumer,
    TenantUserCreateConsumer,
    TenantUserDeleteConsumer,
)
from mapa.manage.messaging.consumer.user_consumers import (
    UserGetConsumer,
    UserFindConsumer,
    UserGetByEmailConsumer,
    UserGetByIdConsumer,
    UserLdapCheckConnectionConsumer,
    UserPasswordCheckConsumer,
    UserGetScopesConsumer,
    UserCreateConsumer,
    UserDeleteConsumer,
    UserPasswordUpdateConsumer,
)
from mapa.manage.messaging.consumer.client_api_consumers import (
    ClientApiCreateConsumer,
    ClientApiDeleteConsumer,
)

from mapa.manage.messaging.consumer.tenant_consumers import (
    TenantFindConsumer,
    TenantGetConsumer,
    TenantPagingConsumer,
    TenantCreateConsumer,
    TenantDeleteConsumer,
    TenantCountConsumer,
)
from mapa.manage.messaging.consumer.tenant_client_consumers import (
    TenantClientGetConsumer,
)

from manage.ldap_server.container import LdapServerContainer
from manage.ping.container import PingContainer
from manage.client.container import ClientContainer
from manage.api.container import ApiContainer
from manage.client_api_scope.container import ClientApiScopeContainer
from manage.api_scope.container import ApiScopeContainer
from manage.client_api.container import ClientApiContainer
from manage.role.container import RoleContainer
from manage.tenant.container import TenantContainer
from manage.user.container import UserContainer
from manage.role_user.container import RoleUserContainer
from manage.role_api_scope.container import RoleApiScopeContainer
from manage.profile_adaptor.container import ProfileAdaptorContainer
from manage.invitation.container import InvitationContainer
from manage.organization.container import OrganizationContainer
from manage.organization_user.container import OrganizationUserContainer
from manage.organization_type.container import OrganizationTypeContainer
from manage.organization_role.container import OrganizationRoleContainer
from manage.organization_client.container import OrganizationClientContainer
from manage.user_variable_type.container import UserVariableTypeContainer
from manage.tenant_user.container import TenantUserContainer
from manage.tenant_client.container import TenantClientContainer


def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]


def get_all_consumers(container, rredis, wredis) -> list:
    connection = container.rabbit_connection()

    return [
        ClientCreateConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiCreateConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ClientApiCreateConsumer(
            container.client_api_package().client_api_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiScopeCreateAllConsumer(
            container.api_scope_package().api_scope_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientApiDeleteConsumer(
            container.client_api_package().client_api_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiDeleteConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ClientDeleteConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientGetByClientIdConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiGetConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ClientDeleteAllConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiDeleteAllConsumer(
            container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiFindConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ClientFindConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientGetInfoConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientGetConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientGetScopesConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiScopeFindConsumer(
            container.api_scope_package().api_scope_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientPagingConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiPagingConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ApiCountConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ApiScopePagingConsumer(
            container.api_scope_package().api_scope_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantGetConsumer(
            container.tenant_package().tenant_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantFindConsumer(
            container.tenant_package().tenant_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantPagingConsumer(
            container.tenant_package().tenant_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantCreateConsumer(
            container.tenant_package().tenant_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantDeleteConsumer(
            container.tenant_package().tenant_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantCountConsumer(
            container.tenant_package().tenant_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantUserFindByUserIdConsumer(
            container.tenant_user_package().tenant_user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantUserCreateConsumer(
            container.tenant_user_package().tenant_user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        TenantUserDeleteConsumer(
            container.tenant_user_package().tenant_user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ClientUpdateConsumer(
            container.client_package().client_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiUpdateConsumer(container.api_package().api_service(), connection=connection, rredis=rredis, wredis=wredis),
        ApiScopeCreateConsumer(
            container.api_scope_package().api_scope_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        ApiScopeDeleteAllConsumer(
            container.api_scope_package().api_scope_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserPasswordUpdateConsumer(container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis),
        UserGetConsumer(container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis),
        UserCreateConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserDeleteConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserFindConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserGetByEmailConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserGetByIdConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserLdapCheckConnectionConsumer(
            container.ldap_server_package().ldap_server_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserPasswordCheckConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        UserGetScopesConsumer(
            container.user_package().user_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        InvitationGetConsumer(
            container.invitation_package().invitation_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        InvitationUpdateConsumer(
            container.invitation_package().invitation_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        OrganizationCreateConsumer(
            container.organization_package().organization_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
        OrganizationDeleteConsumer(
            container.organization_package().organization_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
        OrganizationUserCreateConsumer(
            container.organization_user_package().organization_user_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
        OrganizationUserDeleteConsumer(
            container.organization_user_package().organization_user_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
        OrganizationTypeCreateConsumer(
            container.organization_type_package().organization_type_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
        OrganizationTypeDeleteConsumer(
            container.organization_type_package().organization_type_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
        TenantClientGetConsumer(
            container.tenant_client_package().tenant_client_service(),
            connection=connection, rredis=rredis, wredis=wredis,
        ),
    ]


class AppContainer(containers.DeclarativeContainer):
    """Genel uygulama servis ve DI konteyner yapısı.
    Uygulamadaki veritabanı bağlantısı, alt konteynerlar ve bunların
    birbirlerine olan bağımlılıkları burada tanımlanır.
    """

    # Genel uygulama konfigürasyon bilgileri
    config = providers.Configuration(yaml_files=get_config_file_names(), strict=True)

    # Veritabanı
    db = providers.Singleton(AsyncDatabase, db_url=config.db.url)

    rabbit_connection = providers.Singleton(RabbitConnection, config=config.rabbitmq)

    # Ping package
    ping_package = providers.Container(PingContainer, database=db.provided)

    tenant_package = providers.Container(TenantContainer, database=db.provided)

    tenant_user_package = providers.Container(TenantUserContainer, database=db.provided)

    tenant_client_package = providers.Container(
        TenantClientContainer, database=db.provided
    )

    api_scope_package = providers.Container(ApiScopeContainer, database=db.provided)

    client_api_package = providers.Container(ClientApiContainer, database=db.provided)

    client_package = providers.Container(
        ClientContainer,
        database=db.provided,
        tenant_client_service=tenant_package.tenant_client_service,
        client_api_service=client_api_package.client_api_service,
    )

    api_package = providers.Container(ApiContainer, database=db.provided)

    client_api_scope_package = providers.Container(
        ClientApiScopeContainer, database=db.provided
    )

    client_api_package = providers.Container(ClientApiContainer, database=db.provided)

    role_package = providers.Container(RoleContainer, database=db.provided)

    organization_client_package = providers.Container(
        OrganizationClientContainer, database=db.provided
    )

    organization_package = providers.Container(
        OrganizationContainer,
        database=db.provided,
        organization_client_service=organization_client_package.organization_client_service,
    )

    user_package = providers.Container(
        UserContainer,
        database=db.provided,
        api_service=api_package.api_service,
        organization_service=organization_package.organization_service,
    )

    role_user_package = providers.Container(RoleUserContainer, database=db.provided)

    role_api_scope_package = providers.Container(
        RoleApiScopeContainer, database=db.provided
    )

    profile_adaptor_package = providers.Container(
        ProfileAdaptorContainer, database=db.provided
    )

    organization_user_package = providers.Container(
        OrganizationUserContainer, database=db.provided
    )

    organization_type_package = providers.Container(
        OrganizationTypeContainer, database=db.provided
    )

    organization_role_package = providers.Container(
        OrganizationRoleContainer, database=db.provided
    )

    organization_client_package = providers.Container(
        OrganizationClientContainer, database=db.provided
    )

    user_variable_type_package = providers.Container(
        UserVariableTypeContainer, database=db.provided
    )

    ldap_server_package = providers.Container(
        LdapServerContainer,
        database=db.provided,
        user_service=user_package.user_service,
        tenant_service=tenant_package.tenant_service,
        tenant_user_service=tenant_package.tenant_user_service,
        organization_service=organization_package.organization_service,
        organization_user_service=organization_user_package.organization_user_service,
        organization_type_service=organization_type_package.organization_type_service,
        client_service=client_package.client_service,
    )

    # Invitation Util Service
    invitation_util_service = providers.Singleton(
        InvitationUtilService,
        jwt_secret=config.oidc.jwt_secret,
        user_service=user_package.user_service,
        tenant_user_service=tenant_package.tenant_user_service,
        organization_service=organization_package.organization_service,
        organization_user_service=organization_user_package.organization_user_service,
    )

    invitation_package = providers.Container(
        InvitationContainer,
        database=db.provided,
        config=config,
        invitation_util_service=invitation_util_service,
    )
