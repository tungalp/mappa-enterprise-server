from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint


class RegisterEndpoint(AuthorizeEndpoint):
    """"Register parametreleri"""

    name: str
    surname: str
    email: str
    password: str
    phone: str | None = None
