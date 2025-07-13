from typing import List
from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.manage.constants import LevelTypes
from mapa.manage.organization_client.organization_client_model import CreateOrganizationClient, UpdateAllOrganizationClient, UpdateOrganizationClient, OrganizationClient
from mapa.manage.organization_client.organization_client_repository import OrganizationClientRepository

class OrganizationClientService(BaseEntityService[OrganizationClientRepository, OrganizationClient, CreateOrganizationClient, UpdateOrganizationClient, UpdateAllOrganizationClient]):
    """OrganizationClient Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationClientRepository, OrganizationClient)

    
    async def get_by_organization_client_id(self, organization_client_id: UUID, tenant_id: str = None) -> OrganizationClient:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await super().get(organization_client_id, tenant_id)
    
    
    async def create(self, organization_client: CreateOrganizationClient, tenant_id: str | None = None) -> OrganizationClient:
        """Organization Client oluştururken First_Party clientlar için kontrol yapılır."""
        query_args: QueryArgs = QueryArgs(
                where=[
                    Filter(field="client.client_id", op=FilterOp.EQUAL, value=organization_client.client_id)  ,
                    Filter(field="client.level_type", op=FilterOp.EQUAL, value=LevelTypes.FIRST_PARTY)  
                ],
                select=[
                        "id","organization_id","client_id","is_hierarchical",
                        "client.name","client.client_id","client.client_secret","client.grant_types","client.application_type"
                    ],
                limit=0,
                offset=0
            )
        first_party_client = await super().find(query_args,tenant_id)
        if first_party_client and len(first_party_client) > 0:
            raise ValueError("cannotAssignFirstParty")
        
        created_organization_client: OrganizationClient = await super().create(organization_client, tenant_id)
        return created_organization_client

    async def create_all(self, organization_clients: List[CreateOrganizationClient], tenant_id: str | None = None) -> List[OrganizationClient]:
        """Organization Client oluştururken First_Party clientlar için kontrol yapılır."""
        for organization_client in organization_clients:
            query_args: QueryArgs = QueryArgs(
                where=[
                    Filter(field="client.client_id", op=FilterOp.EQUAL, value=organization_client.client_id)  ,
                    Filter(field="client.level_type", op=FilterOp.EQUAL, value=LevelTypes.FIRST_PARTY)  
                ],
                select=[
                        "id","organization_id","client_id","is_hierarchical",
                        "client.name","client.client_id","client.client_secret","client.grant_types","client.application_type"
                    ],
                limit=0,
                offset=0
            )
            first_party_client = await super().find(query_args,tenant_id)
            if first_party_client and len(first_party_client) > 0:
                raise ValueError("cannotAssignFirstParty")
            
        created_organization_clients = await super().create_all(organization_clients, tenant_id)
        return created_organization_clients