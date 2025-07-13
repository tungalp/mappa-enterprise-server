from sqlalchemy import Enum

class LdapAutoBindOptions:
    DEFAULT = 'DEFAULT'
    NONE = 'NONE'
    NO_TLS = 'NO_TLS'
    TLS_BEFORE_BIND = 'TLS_BEFORE_BIND'
    TLS_AFTER_BIND = 'TLS_AFTER_BIND'


class LdapAuthenticationOptions:
    ANONYMOUS = 'ANONYMOUS'
    SIMPLE = 'SIMPLE'
    NTLM = 'NTLM'
    SASL = 'SASL'


class LdapGetInfoOptions:
    NO_INFO = 'NO_INFO'
    DSA = 'DSA'
    SCHEMA = 'SCHEMA'
    ALL = 'ALL'
    
class ApplicationTypes:
    """ApplicationTypes"""

    SINGLE_PAGE_APPLICATION = "spa"
    WEB = "web"
    NON_INTERACTIVE = "non_interactive"
    NATIVE = "native"


class PromptModes:
    """PromptModes"""

    NONE = "none"
    LOGIN = "login"
    CONSENT = "consent"
    SELECT_ACCOUNT = "select_account"
    REGISTER = "register"


class Algorithms:
    """Algorithms"""

    NONE = "none"

    class Symmetric:
        """Symmetric"""

        HS256 = "HS256"
        HS384 = "HS284"
        HS512 = "HS512"

    class Asymmetric:
        """Asymmetric"""

        RS256 = "RS256"
        RS384 = "RS384"
        RS512 = "RS512"

        ES256 = "ES256"
        ES384 = "ES384"
        ES512 = "ES512"

        PS256 = "PS256"
        PS384 = "PS384"
        PS512 = "PS512"


class GrantTypes:
    """GrandTypes"""
    PASSWORD = "password"
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"
    HYBRID = "hybrid"
    SAML2_BEARER = "urn:ietf:params:oauth:grant-type:saml2-bearer"
    JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"
    TOKEN_EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
    CIBA = "urn:openid:params:grant-type:ciba"
    MFA = "mfa"
    PASSWORDLESS_OTP = "passwordless_otp"


class LevelTypes:
    """LevelTypes"""
    FIRST_PARTY = "FIRST_PARTY"
    SECOND_PARTY = "SECOND_PARTY"
    THIRD_PARTY = "THIRD_PARTY"

class ApiScopeType:
  QUERY_API = 'query:api'
  EDIT_API = 'edit:api'
  QUERY_API_SCOPE = 'query:api_scope'
  EDIT_API_SCOPE = 'edit:api_scope'
  QUERY_CLIENT = 'query:client'
  EDIT_CLIENT = 'edit:client'
  QUERY_CLIENT_API = 'query:client_api'
  EDIT_CLIENT_API = 'edit:client_api'
  QUERY_CLIENT_API_SCOPE = 'query:client_api_scope'
  EDIT_CLIENT_API_SCOPE = 'edit:client_api_scope'
  QUERY_INVITATION = 'query:invitation'
  EDIT_INVITATION = 'edit:invitation'
  QUERY_PROFILE_ADAPTOR = 'query:profile_adaptor'
  EDIT_PROFILE_ADAPTOR = 'edit:profile_adaptor'
  QUERY_ROLE = 'query:role'
  EDIT_ROLE = 'edit:role'
  QUERY_ROLE_API_SCOPE = 'query:role_api_scope'
  EDIT_ROLE_API_SCOPE = 'edit:role_api_scope'
  QUERY_ROLE_USER = 'query:role_user'
  EDIT_ROLE_USER = 'edit:role_user'
  QUERY_USER = 'query:user'
  EDIT_USER = 'edit:user'
  QUERY_ORGANIZATION = 'query:organization'
  EDIT_ORGANIZATION = 'edit:organization'
  QUERY_ORGANIZATION_USER = 'query:organization_user'
  EDIT_ORGANIZATION_USER = 'edit:organization_user'
  QUERY_ORGANIZATION_TYPE = 'query:organization_type'
  EDIT_ORGANIZATION_TYPE = 'edit:organization_type'
  QUERY_ORGANIZATION_ROLE = 'query:organization_role'
  EDIT_ORGANIZATION_ROLE = 'edit:organization_role'
  QUERY_ORGANIZATION_CLIENT = 'query:organization_client'
  EDIT_ORGANIZATION_CLIENT = 'edit:organization_client'
  QUERY_USERVARIABLETYPE = 'query:user_variable_type'
  EDIT_USERVARIABLETYPE = 'edit:user_variable_type'
  QUERY_LDAP_SERVER = 'query:ldap_server'
  EDIT_LDAP_SERVER = 'edit:ldap_server'


client_tenant_client_field_list = [
    'id',
    'client_id',
    'tenant_id',
    'created_at',
    'client.id',
    'client.name',
    'client.client_id',
    'client.client_secret',
    'client.redirect_uris',
    'client.logout_uris',
    'client.client_uri',
    'client.description',
    'client.application_type',
    'client.logo_url',
    'client.token_endpoint_auth_method',
    'client.web_origins',
    'client.cors_origins',
    'client.require_consent',
    'client.is_system',
    'client.require_pkce',
    'client.grant_types',
    'client.level_type',
    'client.created_at',
]

api_field_list = [
    "id",
    "name",
    "identifier",
    "allow_offline_access",
    "skip_consent_for_verifiable_first_party_clients",
    "token_lifetime",
    "token_lifetime_for_web",
    "signing_alg",
    "is_system",
    "api_scopes.id",
    "api_scopes.name",
    "api_scopes.description",
    "api_scopes.api_id",
    "client_api.id",
    "client_api.api_id",
    "client_api.client_id"
]

app_field_list = [
    "id",
    "name",
    "title",
    "description",
    "logo",
    "menu",
    "translation",
    "client_id",
    "api_id",
    "logout_uri",
    "return_uri",
    "client_secret",
    "identifier",
    "tenant_id",
    "content_page.id",
    "content_page.type",
    "content_page.name",
    "content_page.title",
    "content_page.description",
    "content_page.scope",
    "content_page.designer_schema",
    "content_page.path",
    "content_page.query"
]
