from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint


class LoginEndpoint(AuthorizeEndpoint):
    """"Login parametreleri"""

    email: str
    password: str