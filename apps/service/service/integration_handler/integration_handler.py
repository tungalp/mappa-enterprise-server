from typing import Any, Dict

from mapa.gateway.integration.integration_model import Integration

from mapa.gateway.route.route_model import Route
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse

class IntegrationHandler:
    """Integration BaseClass"""

    integration: Integration
    
    def __init__(
        self,
        route: Route,
        path_params: Dict[str, Any]
    ) -> None:
        self.route = route
        self.integration = route.integration # type: ignore
        self.path_params = path_params

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        raise NotImplementedError()
