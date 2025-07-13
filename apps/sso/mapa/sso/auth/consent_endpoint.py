from xmlrpc.client import boolean
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint


class ConsentEndpoint(AuthorizeEndpoint):
    """"Consent parametreleri"""

    accepted: boolean
    language: str
