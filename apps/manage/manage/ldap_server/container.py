from dependency_injector import containers, providers
from mapa.manage.ldap_server.ldap_server_service import LdapServerService


class LdapServerContainer(containers.DeclarativeContainer):
    """LdapServer paketinin bağımlılık konteyneri"""

    database = providers.Dependency()
    ldap_server_client_service = providers.Dependency()
    user_service = providers.Dependency()
    client_service = providers.Dependency()
    tenant_service = providers.Dependency()
    tenant_user_service = providers.Dependency()
    organization_service = providers.Dependency()
    organization_type_service = providers.Dependency()
    organization_user_service = providers.Dependency()

    ldap_server_service = providers.Factory(
        LdapServerService,
        async_db=database,
        user_service=user_service,
        client_service = client_service,
        tenant_service=tenant_service,
        tenant_user_service=tenant_user_service,
        organization_type_service=organization_type_service,
        organization_service=organization_service,
        organization_user_service=organization_user_service,
    )
