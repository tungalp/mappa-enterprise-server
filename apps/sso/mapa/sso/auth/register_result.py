from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.sso.models import TenantUser


class RegisterResult:
    """Register işleminin dönüş değeri"""
    
    def __init__(self, register_endpoint: RegisterEndpoint, tenant_user: TenantUser) -> None:
        self._register_endpoint = register_endpoint
        self._tenant_user = tenant_user
        
    def execute(self):
        return {
            "type": "json",
            "data": {
                "user_id": str(self._tenant_user.user_id),
                "state": self._register_endpoint.state
            }
        }