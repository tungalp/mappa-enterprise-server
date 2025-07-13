from uuid import UUID
from nanoid import generate
from typing import Any, List, Optional
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.gateway.constant import LevelTypes
from mapa.gateway.gateway_api.gateway_api_model import (
    CreateGatewayApi,
    UpdateAllGatewayApi,
    UpdateGatewayApi,
    GatewayApi,
)
from mapa.gateway.gateway_api.gateway_api_repository import GatewayApiRepository

from mapa.gateway.messaging.producer.service_messenger import ServiceMessenger
from mapa.gateway.models import CreateApi, UpdateApi


class GatewayApiService(
    BaseEntityService[
        GatewayApiRepository,
        GatewayApi,
        CreateGatewayApi,
        UpdateGatewayApi,
        UpdateAllGatewayApi,
    ]
):
    """Api Servisi"""

    def __init__(self, async_db: AsyncDatabase, messenger: ServiceMessenger) -> None:
        self.async_db = async_db
        self.messenger = messenger
        super().__init__(async_db, GatewayApiRepository, GatewayApi)

    async def create(
        self, gateway_api: CreateGatewayApi, tenant_id: str | None = None
    ) -> GatewayApi:
        """Api oluştururken manage api oluşturarak kaydeder."""
        created_api_id_list = []
        try:
            manage_api = generate_api()
            manage_api.identifier = gateway_api.identifier
            manage_api.level_type = LevelTypes.SECOND_PARTY
            manage_api.name = gateway_api.name
            created_manage_api = await self.messenger.create_api(
                manage_api.model_dump(), tenant_id
            )
            gateway_api.manage_api_id = created_manage_api["id"]
            created_api_id_list.append(created_manage_api["id"])

            api = await super().create(gateway_api, tenant_id)
            return api
        except Exception as Ex:
            if len(created_api_id_list) > 0:
                query_args: QueryArgs = QueryArgs(
                    where=[
                        Filter(field="id", op=FilterOp.IN, value=created_api_id_list)
                    ],
                    limit=0,
                    offset=0,
                )
                await self.messenger.delete_all_apis(
                    query_args.to_serialize(), tenant_id
                )

            raise Ex

    async def create_all(
        self, gateway_apis: List[CreateGatewayApi], tenant_id: str | None = None
    ) -> List[GatewayApi]:
        """Api oluştururken manage api oluşturarak kaydeder."""
        created_api_id_list = []
        try:
            for gateway_api in gateway_apis:
                manage_api = generate_api()
                manage_api.identifier = gateway_api.identifier
                manage_api.level_type = LevelTypes.SECOND_PARTY
                manage_api.name = gateway_api.name
                created_manage_api = await self.messenger.create_api(
                    manage_api.model_dump(), tenant_id
                )
                gateway_api.manage_api_id = created_manage_api["id"]
                created_api_id_list.append(created_manage_api["id"])

            apis = await super().create_all(gateway_apis, tenant_id)
            return apis
        except Exception as Ex:
            if len(created_api_id_list) > 0:
                query_args: QueryArgs = QueryArgs(
                    where=[
                        Filter(field="id", op=FilterOp.IN, value=created_api_id_list)
                    ],
                    limit=0,
                    offset=0,
                )
                await self.messenger.delete_all_apis(
                    query_args.to_serialize(), tenant_id
                )

            raise Ex

    async def delete_by_ids(
        self, obj_ids: List[Any], tenant_id: str | None = None
    ) -> int:
        """Gelen id listesindeki kayıtların manage apilerini daha sonra gateway apilerini siler."""
        query_args: QueryArgs = QueryArgs(
            where=[
                Filter(field="id", op=FilterOp.IN, value=obj_ids),
            ],
            limit=0,
            offset=0,
        )
        gateway_apis = await super().paging(query_args, tenant_id)
        for gateway_api in gateway_apis.items:
            await self.messenger.delete_api(gateway_api.manage_api_id, tenant_id)
        return await super().delete_by_ids(obj_ids, tenant_id)

    async def delete_all(
        self, query_args: QueryArgs, tenant_id: str | None = None
    ) -> int:
        """Gelen query_args parametresin ile eşleşen kayıtların manage apilerini daha sonra gateway apilerini siler."""
        query_args.offset = 0
        query_args.limit = 0
        gateway_apis = await super().paging(query_args, tenant_id)
        for gateway_api in gateway_apis.items:
            await self.messenger.delete_api(gateway_api.manage_api_id, tenant_id)
        return await super().delete_all(query_args, tenant_id)

    async def delete(self, obj_id: Any, tenant_id: str | None = None) -> bool:
        """Gelen id ile kaydın manage api daha sonra gateway api'sini siler."""
        query_args: QueryArgs = QueryArgs(
            where=[
                Filter(field="id", op=FilterOp.EQUAL, value=obj_id),
            ],
            limit=0,
            offset=0,
        )
        gateway_apis = await super().paging(query_args, tenant_id)
        for gateway_api in gateway_apis.items:
            await self.messenger.delete_api(gateway_api.manage_api_id, tenant_id)
        return await super().delete(obj_id, tenant_id)

    async def update(
        self, obj_id: Any, input_obj: UpdateGatewayApi, tenant_id: str | None = None
    ) -> GatewayApi | None:
        """Verilen modeli günceller"""

        orjinal_gateway_api = await super().get(obj_id, tenant_id)
        manage_api = None
        try:
            if input_obj.name and len(input_obj.name) > 0:
                if orjinal_gateway_api and orjinal_gateway_api.manage_api_id:
                    manage_api = await self.messenger.get_api(
                        str(orjinal_gateway_api.manage_api_id),
                        tenant_id,
                        [
                            "id",
                            "name",
                            "identifier",
                            "allow_offline_access",
                            "skip_consent_for_verifiable_first_party_clients",
                            "token_lifetime",
                            "token_lifetime_for_web",
                            "signing_alg",
                            "is_system",
                        ],
                    )
                    if manage_api:
                        update_manage_api = generate_update_api(input_obj.name)
                        await self.messenger.update_api(
                            manage_api["id"], update_manage_api.model_dump(exclude_none=True), tenant_id
                        )

            return await super().update(obj_id, input_obj, tenant_id)
        except Exception as Ex:
            if orjinal_gateway_api:
                await super().update(
                    obj_id, converted_update_gateway_api(orjinal_gateway_api), tenant_id
                )
            if manage_api is not None:
                update_manage = generate_update_api(orjinal_gateway_api.name)
                await self.messenger.update_api(
                    manage_api["id"], update_manage.model_dump(exclude_none=True), tenant_id
                )

            raise Ex

    async def update_by_ids(
        self,
        obj_ids: List[Any],
        input_obj: UpdateGatewayApi,
        tenant_id: str | None = None,
    ) -> bool:
        """Verilen modeli günceller"""
        if input_obj.name and len(input_obj.name) > 0:
            query_args: QueryArgs = QueryArgs(
                where=[
                    Filter(field="id", op=FilterOp.IN, value=obj_ids),
                ],
                limit=0,
                offset=0,
            )
            gateway_apis = await super().paging(query_args, tenant_id)
            for gateway_api in gateway_apis.items:
                if gateway_api and gateway_api.manage_api_id:
                    manage_api = await self.messenger.get_api(
                        str(gateway_api.manage_api_id),
                        tenant_id,
                        [
                            "id",
                            "name",
                            "identifier",
                            "allow_offline_access",
                            "skip_consent_for_verifiable_first_party_clients",
                            "token_lifetime",
                            "token_lifetime_for_web",
                            "signing_alg",
                            "is_system",
                        ],
                    )
                    if manage_api:
                        update_manage_api = generate_update_api(input_obj.name)
                        await self.messenger.update_api(
                            manage_api["id"], update_manage_api.model_dump(exclude_none=True), tenant_id
                        )

        return await super().update_by_ids(obj_ids, input_obj, tenant_id)


def generate_api() -> CreateApi:
    return CreateApi(name="", identifier="")


def generate_update_api(name: str) -> UpdateApi:
    return UpdateApi(name=name)


def converted_update_gateway_api(orjinal_gateway_api: GatewayApi) -> UpdateGatewayApi:
    return UpdateGatewayApi(
        name=orjinal_gateway_api.name,
        description=orjinal_gateway_api.description,
        path=orjinal_gateway_api.path,
        identifier=orjinal_gateway_api.identifier,
        context=orjinal_gateway_api.context,
    )
