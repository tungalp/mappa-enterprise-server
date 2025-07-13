from service.model.custom_response import CustomResponse
from zeep.transports import Transport
from httpx import AsyncClient as HttpxAsyncClient


class AsyncTransport(Transport):
    def __init__(self, async_client: HttpxAsyncClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_client = async_client

    async def post(self, address, message, headers):
        response = await self.async_client.post(address, content=message, headers=headers)
        return CustomResponse(response)

    async def get(self, address, params, headers):
        response = await self.async_client.get(address, params=params, headers=headers)
        return CustomResponse(response)
