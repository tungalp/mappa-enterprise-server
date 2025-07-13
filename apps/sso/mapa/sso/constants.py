from typing import List

class ResponseTypes:
    """Authorize servis metodu dönüş tipleri
    """
    CODE = "code"
    TOKEN = "token"
    IDTOKEN = "id_token"
    IDTOKEN_TOKEN = "id_token token"
    CODE_IDTOKEN = "code id_token"
    CODE_TOKEN = "code token"
    CODE_IDTOKEN_TOKEN = "code id_token token"

    @classmethod
    def to_list(cls) -> List[str]:
        """Dönüş tipleri liste olarak döndürülür"""
        return [
            cls.CODE, cls.CODE_IDTOKEN, cls.CODE_IDTOKEN_TOKEN,
            cls.IDTOKEN, cls.IDTOKEN_TOKEN
        ]


class TokenTypes:
    """TokenTypes"""

    ACCESS_TOKEN = "access_token"
    IDENTITY_TOKEN = "id_token"
    REFRESH_TOKEN = "refresh_token"


class EndpointAuthenticationMethods:
    """EndpointAuthenticationMethods"""

    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_BASIC = "client_secret_basic"
    PRIVATE_KEY_JWT = "private_key_jwt"
    TLS_CLIENT_AUTH = "tls_client_auth"
    SELF_SIGNED_TLS_CLIENT_AUTH = "self_signed_tls_client_auth"


class TokenTypeIdentifiers:
    """TokenTypeIdentifiers"""

    ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
    IDENTITY_TOKEN = "urn:ietf:params:oauth:token-type:id_token"
    REFRESH_TOKEN = "urn:ietf:params:oauth:token-type:refresh_token"
    SAML11 = "urn:ietf:params:oauth:token-type:saml1"
    SAML2 = "urn:ietf:params:oauth:token-type:saml2"
    JWT = "urn:ietf:params:oauth:token-type:jwt"


class ProtocolRoutePaths:
    """ProtocolRoutePaths"""

    CONNECT_PATH_PREFIX = "oidc"

    AUTHORIZE = CONNECT_PATH_PREFIX + "/authorize"
    AUTHORIZE_CALLBACK = AUTHORIZE + "/callback"
    DISCOVERY_CONFIGURATION = CONNECT_PATH_PREFIX + \
        "/.well-known/openid-configuration"
    DISCOVERY_WEB_KEYS = CONNECT_PATH_PREFIX + "/jwks"
    BACKCHANNEL_AUTHENTICATION = CONNECT_PATH_PREFIX + "/ciba"
    TOKEN = CONNECT_PATH_PREFIX + "/token"
    REVOCATION = CONNECT_PATH_PREFIX + "/revocation"
    USERINFO = CONNECT_PATH_PREFIX + "/userinfo"
    INTROSPECTION = CONNECT_PATH_PREFIX + "/introspect"
    END_SESSION = CONNECT_PATH_PREFIX + "/endsession"
    END_SESSION_CALLBACK = END_SESSION + "/callback"
    CHECK_SESSION = CONNECT_PATH_PREFIX + "/checksession"
    DEVICE_AUTHORIZATION = CONNECT_PATH_PREFIX + "/deviceauthorization"

    MTLS_PATH_PREFIX = CONNECT_PATH_PREFIX + "/mtls"
    MTLS_TOKEN = MTLS_PATH_PREFIX + "/token"
    MTLS_REVOCATION = MTLS_PATH_PREFIX + "/revocation"
    MTLS_INTROSPECTION = MTLS_PATH_PREFIX + "/introspect"
    MTLS_DEVICE_AUTHORIZATION = MTLS_PATH_PREFIX + "/deviceauthorization"


class AuthorizeErrors:
    """Athorize servis metodu hata kodları"""

    #  OAuth2 errors
    INVALID_REQUEST = "invalid_request"
    INVALID_CLIENT = "invalid_client"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    ACCESS_DENIED = "access_denied"
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
    UNSUPPORTED_RESPONSE_MODE = "unsupported_response_mode"
    INVALID_SCOPE = "invalid_scope"
    SERVER_ERROR = "server_error"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"

    # OIDC errors
    INTERACTION_REQUIRED = "interaction_required"
    LOGIN_REQUIRED = "login_required"
    ACCOUNT_SELECTION_REQUIRED = "account_selection_required"
    CONSENT_REQUIRED = "consent_required"
    INVALID_REQUEST_URI = "invalid_request_uri"
    INVALID_REQUEST_OBJECT = "invalid_request_object"
    REQUEST_NOT_SUPPORTED = "request_not_supported"
    REQUEST_URI_NOT_SUPPORTED = "request_uri_not_supported"
    REGISTRATION_NOT_SUPPORTED = "registration_not_supported"

    # resource indicator spec
    INVALID_TARGET = "invalid_target"
    
    NONCE_VALUE_REQUIRED = "nonce_value_required"
    INVALID_REDIRECT_URI = "invalid_redirect_uri"
    
    INSECURE_TRANSPORT = "insecure_transport"
    SESSION_NOT_FOUND = "session_not_found"


class BackchannelAuthenticationRequestErrors:
    """BackchannelAuthenticationRequestErrors"""

    INVALID_REQUEST_OBJECT = "invalid_request_object"
    INVALID_REQUEST = "invalid_request"
    INVALID_SCOPE = "invalid_scope"
    EXPIRED_LOGIN_HINT_TOKEN = "expired_login_hint_token"
    UNKNOWN_USER_ID = "unknown_user_id"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    MISSING_USER_CODE = "missing_user_code"
    INVALID_USER_CODE = "invalid_user_code"
    INVALID_BINDING_MESSAGE = "invalid_binding_message"
    INVALID_CLIENT = "invalid_client"
    ACCESS_DENIED = "access_denied"
    INVALID_TARGET = "invalid_target"


class AuthorizationErrors:
    """AuthorizationErrors"""
    
    MISSING_AUTHORIZATION = "missing_authorization"
    INSECURE_TRANSPORT = "insecure_transport"
    
    
class TokenErrors:
    """TokenErrors"""

    INVALID_REQUEST = "invalid_request"
    INVALID_CLIENT = "invalid_client"
    INVALID_GRANT = "invalid_grant"
    INVALID_TOKEN = "invalid_token"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
    INVALID_SCOPE = "invalid_scope"
    AUTHORIZATION_PENDING = "authorization_pending"
    ACCESS_DENIED = "access_denied"
    SLOW_DOWN = "slow_down"
    EXPIRED_TOKEN = "expired_token"
    INVALID_TARGET = "invalid_target"
    MISMATCHING_STATE = "mismatching_state"
    MISSING_TOKEN = "missing_token"
    MISSING_TOKEN_TYPE = "missing_token_type"
    UNSUPPORTED_TOKEN_TYPE = "unsupported_token_type"
    MISSING_CODE = "missing_code"


class ProtectedResourceErrors:
    """ProtectedResourceErrors"""

    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    INVALID_REQUEST = "invalid_request"
    INSUFFICIENT_SCOPE = "insufficient_scope"


class TokenRequestTypes:
    """TokenRequestTypes"""

    BEARER = "bearer"
    POP = "pop"


class AuthenticationSchemes:
    """AuthenticationSchemes"""

    AuthorizationHeaderBearer = "Bearer"
    FormPostBearer = "access_token"
    QueryStringBearer = "access_token"
    AuthorizationHeaderPop = "PoP"
    FormPostPop = "pop_access_token"
    QueryStringPop = "pop_access_token"


class ClientAssertionTypes:
    """ClientAssertionTypes"""

    JWT_BEARER = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    SAML_BEARER = "urn:ietf:params:oauth:client-assertion-type:saml2-bearer"


class ResponseModes:
    """Authorize servisi dönüş değeri modu"""

    FORM_POST = "form_post"
    QUERY = "query"
    FRAGMENT = "fragment"
    WEB_MESSAGE = "web_message"

    @classmethod
    def to_list(cls) -> List[str]:
        """Dönüş tipleri liste olarak döndürülür"""
        return [
            cls.FORM_POST, cls.QUERY, cls.FRAGMENT, cls.WEB_MESSAGE
        ]


class DisplayModes:
    """DisplayModes"""

    PAGE = "page"
    POPUP = "popup"
    TOUCH = "touch"
    WAP = "wap"


class PromptModes:
    """PromptModes"""

    NONE = "none"
    LOGIN = "login"
    CONSENT = "consent"
    SELECT_ACCOUNT = "select_account"
    REGISTER = "register"


class CodeChallengeMethods:
    """CodeChallengeMethods"""

    PLAIN = "plain"
    SHA256 = "S256"


class AuthenticationMethods:
    """AuthenticationMethods"""

    FACIAL_RECOGNITION = "face"
    FINGERPRINT_BIOMETRIC = "fpt"
    GEOLOCATION = "geo"
    PROOF_OF_POSSESSION_HARDWARE_SECURED_KEY = "hwk"
    IRIS_SCAN_BIOMETRIC = "iris"
    KNOWLEDGE_BASED_AUTHENTICATION = "kba"
    MULTIPLE_CHANNEL_AUTHENTICATION = "mca"
    MULTI_FACTOR_AUTHENTICATION = "mfa"
    ONE_TIME_PASSWORD = "otp"
    PERSONAL_IDENTIFICATION_OR_PATTERN = "pin"
    PASSWORD = "pwd"
    RISK_BASED_AUTHENTICATION = "rba"
    RETINA_SCAN_BIOMETRIC = "retina"
    SMART_CARD = "sc"
    CONFIRMATION_BY_SMS = "sms"
    PROOF_OF_POSSESSION_SOFTWARE_SECURED_KEY = "swk"
    CONFIRMATION_BY_TELEPHONE = "tel"
    USER_PRESENCE_TEST = "user"
    VOICE_BIOMETRIC = "vbm"
    WINDOWS_INTEGRATED_AUTHENTICATION = "wia"

class Discovery:
    """Discovery Document"""

    Issuer = "issuer"

    # endpoints
    AUTHORIZATION_ENDPOINT = "authorization_endpoint"
    DEVICE_AUTHORIZATION_ENDPOINT = "device_authorization_endpoint"
    TOKEN_ENDPOINT = "token_endpoint"
    USERINFO_ENDPOINT = "userinfo_endpoint"
    INTROSPECTION_ENDPOINT = "introspection_endpoint"
    REVOCATION_ENDPOINT = "revocation_endpoint"
    JwksUri = "jwks_uri"
    END_SESSION_ENDPOINT = "end_session_endpoint"
    CHECK_SESSION_IFRAME = "check_session_iframe"
    REGISTRATION_ENDPOINT = "registration_endpoint"
    MTLS_ENDPOINT_ALIASES = "mtls_endpoint_aliases"

    # common capabilities
    FRONTCHANNEL_LOGOUT_SUPPORTED = "frontchannel_logout_supported"
    FRONTCHANNEL_LOGOUT_SESSION_SUPPORTED = "frontchannel_logout_session_supported"
    BACKCHANNEL_LOGOUT_SUPPORTED = "backchannel_logout_supported"
    BACKCHANNEL_LOGOUT_SESSION_SUPPORTED = "backchannel_logout_session_supported"
    GRANT_TYPES_SUPPORTED = "grant_types_supported"
    CODE_CHALLENGE_METHODS_SUPPORTED = "code_challenge_methods_supported"
    SCOPES_SUPPORTED = "scopes_supported"
    SUBJECT_TYPES_SUPPORTED = "subject_types_supported"
    RESPONSE_MODES_SUPPORTED = "response_modes_supported"
    RESPONSE_TYPES_SUPPORTED = "response_types_supported"
    CLAIMS_SUPPORTED = "claims_supported"
    TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED = "token_endpoint_auth_methods_supported"

    # more capabilities
    CLAIMS_LOCALES_SUPPORTED = "claims_locales_supported"
    CLAIMS_PARAMETER_SUPPORTED = "claims_parameter_supported"
    CLAIM_TYPES_SUPPORTED = "claim_types_supported"
    DISPLAY_VALUES_SUPPORTED = "display_values_supported"
    ACR_VALUES_SUPPORTED = "acr_values_supported"
    ID_TOKEN_ENCRYPTION_ALG_VALUES_SUPPORTED = "id_token_encryption_alg_values_supported"
    ID_TOKEN_ENCRYPTION_ENC_VALUES_SUPPORTED = "id_token_encryption_enc_values_supported"
    ID_TOKEN_SIGNING_ALG_VALUES_SUPPORTED = "id_token_signing_alg_values_supported"
    OP_POLICY_URI = "op_policy_uri"
    OP_TOS_URI = "op_tos_uri"
    REQUEST_OBJECT_ENCRYPTION_ALG_VALUES_SUPPORTED = "request_object_encryption_alg_values_supported"
    REQUEST_OBJECT_ENCRYPTION_ENC_VALUES_SUPPORTED = "request_object_encryption_enc_values_supported"
    REQUEST_OBJECT_SIGNING_ALG_VALUES_SUPPORTED = "request_object_signing_alg_values_supported"
    REQUEST_PARAMETER_SUPPORTED = "request_parameter_supported"
    REQUEST_URI_PARAMETER_SUPPORTED = "request_uri_parameter_supported"
    REQUIRE_REQUEST_URI_REGISTRATION = "require_request_uri_registration"
    SERVICE_DOCUMENTATION = "service_documentation"
    TOKEN_ENDPOINT_AUTH_SIGNING_ALG_VALUES_SUPPORTED = "token_endpoint_auth_signing_alg_values_supported"
    UI_LOCALES_SUPPORTED = "ui_locales_supported"
    USERINFO_ENCRYPTION_ALG_VALUES_SUPPORTED = "userinfo_encryption_alg_values_supported"
    USERINFO_ENCRYPTION_ENC_VALUES_SUPPORTED = "userinfo_encryption_enc_values_supported"
    USERINFO_SIGNING_ALG_VALUES_SUPPORTED = "userinfo_signing_alg_values_supported"
    TLS_CLIENT_CERTIFICATE_BOUND_ACCESS_TOKENS = "tls_client_certificate_bound_access_tokens"
    AUTHORIZATION_RESPONSE_ISS_PARAMETER_SUPPORTED = "authorization_response_iss_parameter_supported"

    # CIBA
    BACKCHANNEL_TOKEN_DELIVERY_MODES_SUPPORTED = "backchannel_token_delivery_modes_supported"
    BACKCHANNEL_AUTHENTICATION_ENDPOINT = "backchannel_authentication_endpoint"
    BACKCHANNEL_AUTHENTICATION_REQUEST_SIGNING_ALG_VALUES_SUPPORTED = "backchannel_authentication_request_signing_alg_values_supported"
    BACKCHANNEL_USER_CODE_PARAMETER_SUPPORTED = "backchannel_user_code_parameter_supported"


class BackchannelTokenDeliveryModes:
    """BackchannelTokenDeliveryModes"""
    POLL = "poll"
    PING = "ping"
    PUSH = "push"


class Events:
    """Events"""
    BACK_CHANNEL_LOGOUT = "http://schemas.openid.net/event/backchannel-logout"


class BackChannelLogoutRequest:
    """BackChannelLogoutRequest"""
    LOGOUT_TOKEN = "logout_token"


class StandardScopes:
    """StandardScopes"""

    OPENID = "openid"
    PROFILE = "profile"
    EMAIL = "email"
    ADDRESS = "address"
    PHONE = "phone"
    OFFLINE_ACCESS = "offline_access"

class SsoConstants:
    """SsoConstants"""

    SESSION_COOKIE_NAME = "_sso_session_"


class LevelTypes:
    """LevelTypes"""
    FIRST_PARTY = "FIRST_PARTY"
    SECOND_PARTY = "SECOND_PARTY"
    THIRD_PARTY = "THIRD_PARTY"
    
    
class ApplicationTypes:
    """ApplicationTypes"""

    SINGLE_PAGE_APPLICATION = "spa"
    WEB = "web"
    NON_INTERACTIVE = "non_interactive"
    NATIVE = "native"


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