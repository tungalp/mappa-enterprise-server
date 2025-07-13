
from .request import ServiceRequest


class FunctionRequest(ServiceRequest):
    """Function Request Modeli"""

    handler: str
    timeout: int = 30
    