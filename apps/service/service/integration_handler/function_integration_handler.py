import json
from typing import Any, Dict

import httpx
from mapa.gateway.integration.integration_model import FunctionConnection
from mapa.gateway.route.route_model import Route
from service.integration_handler.integration_handler import IntegrationHandler
from mapa.service.request import ServiceRequest
from mapa.service.response import ServiceResponse
from mapa.service.function import FunctionRequest


class FunctionIntegrationHandler(IntegrationHandler):
    """Integration handler for function"""

    def __init__(self, route: Route, path_params: Dict[str, Any], runtime_url: str) -> None:
        super().__init__(route, path_params)
        self._runtime_url = runtime_url

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        if not self.integration.connection:
            raise ValueError("Connection not defined")

        function_conn = FunctionConnection(**(self.integration.connection))

        function_request = FunctionRequest(**service_request.model_dump(), handler=function_conn.handler, timeout=function_conn.timeout)

        # Send request to function runtime and get response
        ret_val = None
        async with httpx.AsyncClient(timeout=function_conn.timeout) as client:
            response = await client.post(f"{self._runtime_url}/task/{function_conn.runtime_id}", content=json.dumps(function_request.model_dump()))
            ret_val = ServiceResponse(**response.json())


        return ret_val