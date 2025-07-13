from enum import Enum


class MethodTypes:
    """MethodTypes"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    ANY = "ANY"


class ApiTypes:
    """ApiTypes"""

    HTTP = "HTTP API"


class IntegrationTypes:
    """IntegrationTypes"""

    FUNCTIONS = "Functions"
    HTTP_BACKEND = "HTTPBackend"
    ADHOC_QUERY = "AdHocQuery"
    SOAP_BACKEND = "SoapBackend"
    FILE_BACKEND = "FileBackend"
    ELASTIC_BACKEND = "ElasticBackend"
    MONGO_QUERY = "MongoQuery"
    SPATIAL_BACKEND = "SpatialBackend"


class ParameterMappingTypes:
    """ParameterMappingTypes"""

    REQUEST = "request"
    RESPONSE = "response"


class AuthenticationInfoTypes:
    """AuthenticationInfoTypes"""

    BASICAUTH = "BasicAuth"
    BEARERTOKEN = "BearerToken"
    APIKEY = "ApiKey"


class ConnectionInfoTypes:
    """ConnectionInfoTypes"""

    DATABASE = "Database"
    AUTHENTICATION = "Authentication"


class ApiKeyAddToTypes:
    """ApiKeyAddToTypes"""

    HEADER = ("Header",)
    QUERYPARAMS = ("QueryParams",)


class ParameterTypes:
    """RequestParameterTypes"""

    HEADER = "header"
    QUERY = "query"
    PATH = "path"
    BODY = "body"
    STATUS_CODE = "status_code"


class ModifierTypes:
    """RequestModifierTypes"""

    APPEND = "append"
    OVERWRITE = "overwrite"
    REMOVE = "remove"


class ValueTypes:
    """RequestValueTypes"""

    HEADER = "header"
    QUERY = "query"
    PATH = "path"
    BODY = "body"
    CONTEXT = "context"
    STATIC = "static"


class SqlResultTypes:
    """Sorgu sonuçlarının dönüş şekli"""

    MULTI = "multi"
    SINGLE = "single"


class ApiScopeType:
    QUERY_CONNECTION_INFO = "query:connection_info"
    EDIT_CONNECTION_INFO = "edit:connection_info"
    QUERY_CONTEXT_VAR = "query:context_var"
    EDIT_CONTEXT_VAR = "edit:context_var"
    QUERY_GATEWAY_API = "query:gateway_api"
    EDIT_GATEWAY_API = "edit:gateway_api"
    QUERY_INTEGRATION = "query:integration"
    EDIT_INTEGRATION = "edit:integration"
    QUERY_PARAMETER_MAPPING = "query:parameter_mapping"
    EDIT_PARAMETER_MAPPING = "edit:parameter_mapping"
    QUERY_ROUTE = "query:route"
    EDIT_ROUTE = "edit:route"


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
