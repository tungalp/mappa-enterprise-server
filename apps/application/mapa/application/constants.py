class ContentPageType:
    """ContentPageType"""

    BLANK = "blank"
    PAGE = "page"
    MAP = "map"


class ApiScopeType:
    QUERY_APPLICATION = 'query:application'
    EDIT_APPLICATION = 'edit:application'
    QUERY_CONTENT_PAGE = 'query:content_page'
    EDIT_CONTENT_PAGE = 'edit:content_page'
    QUERY_CONTENT_PAGE_TEMPLATE = 'query:content_page_template'
    EDIT_CONTENT_PAGE_TEMPLATE = 'edit:content_page_template'

    
class ApplicationTypes:
    """ApplicationTypes"""

    SINGLE_PAGE_APPLICATION = "spa"
    WEB = "web"
    NON_INTERACTIVE = "non_interactive"
    NATIVE = "native"


class LevelTypes:
    """LevelTypes"""
    FIRST_PARTY = "FIRST_PARTY"
    SECOND_PARTY = "SECOND_PARTY"
    THIRD_PARTY = "THIRD_PARTY"


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

