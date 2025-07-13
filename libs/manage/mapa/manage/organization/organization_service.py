from typing import Any,List
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from mapa.manage.organization.organization_model import CreateOrganization, Organization, UpdateAllOrganization, UpdateOrganization
from mapa.manage.organization.organization_repository import OrganizationRepository
from uuid import UUID
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.organization_client.organization_client_model import OrganizationClient

class OrganizationService(BaseEntityService[OrganizationRepository, Organization, CreateOrganization, UpdateOrganization, UpdateAllOrganization]):
    """OrganizationService""" 

    def __init__(self, async_db: AsyncDatabase, organization_client_service: OrganizationClientService ) -> None:
        super().__init__(async_db, OrganizationRepository, Organization)
        self.organization_client_service = organization_client_service
        
        
    # sorgulama işlemi yapıldığında bulunan kayıtların parent bilgileride bulunmaktadır.
    # Organization ana page componentinde sorgu için kullanılır.
    async def hierarchical_paging(self, query_args: QueryArgs, tenant_id: str | None = None) -> PagingResult[Organization]:
        organization_list = []
        result = await super().paging(query_args, tenant_id)

        if result and len(result.items) > 0:
            for organization in result.items:
                if any(item.id == organization.id for item in organization_list) is False:
                    organization_list.append(organization)
                await self.get_hierarchical_parent_organization(str(organization.parent_id), organization_list, tenant_id) 
            result.items = organization_list
            result.total = len(organization_list)
        return result  
        
    async def paging(self, query_args: QueryArgs, tenant_id: str | None = None) -> PagingResult[Organization]:
        result = await super().paging(query_args, tenant_id)
        return result    

    # Organization bilgisinde root kaydın silinmemesi için kontrol eklendi.
    # Silinmek istenen Organization'ın childları da listeye dahil edildi.
    async def delete_by_ids(self, obj_ids: List[Any], tenant_id: str | None = None) -> int:
        organization_list = []
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.IN, value=obj_ids),
        ], limit=0, offset=0)
        organizations = await super().paging(query_args, tenant_id)
        
        if organizations is not None and len(organizations.items) > 0:
            for organization in organizations.items:
                organization_list.append(organization) 
                await self.get_hierarchical_child_organization(str(organization.id), organization_list, tenant_id)
        
        filtered_list = [item for item in organization_list if item.is_root == True]
        if len(filtered_list) > 0:
            raise ValueError("rootNotDeleted")
        
        obj_ids.clear()
        for item in organization_list:
            obj_ids.append(item.id)    
            
        return await super().delete_by_ids(obj_ids, tenant_id)

    # Organization bilgisinde root kaydın silinmemesi için kontrol eklendi.
    # Silinmek istenen Organization'ın childları da listeye dahil edildi.
    async def delete_all(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        organization_list = []
        query_args.offset = 0
        query_args.limit = 0
        organizations = await super().paging(query_args, tenant_id)
        
        if organizations is not None and len(organizations.items) > 0:
            for organization in organizations.items:
                organization_list.append(organization) 
                await self.get_hierarchical_child_organization(str(organization.id), organization_list, tenant_id)
        
        filtered_list = [item for item in organization_list if item.is_root == True]
        if len(filtered_list) > 0:
            raise ValueError("rootNotDeleted")
        
        if query_args.where is None or len(query_args.where)==0:
            query_args.where = []
                
        for filter in query_args.where:
            if filter and filter.model_dump().get("field") == "id":
                filter.value = [item.id for item in organization_list]
        
        return await super().delete_all(query_args, tenant_id)

    # Organization bilgisinde root kaydın silinmemesi için kontrol eklendi.
    # Silinmek istenen Organization'ın childları da listeye dahil edildi.
    async def delete(self, obj_id: Any, tenant_id: str | None = None) -> bool:
        organization_list = []
        obj_ids=[]
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=obj_id),
        ], limit=0, offset=0)
        organizations = await super().paging(query_args, tenant_id)
        
        if organizations is not None and len(organizations.items) > 0:
            for organization in organizations.items:
                organization_list.append(organization) 
                await self.get_hierarchical_child_organization(str(organization.id), organization_list, tenant_id)
                
        filtered_list = [item for item in organization_list if item.is_root == True]
        if len(filtered_list) > 0:
            raise ValueError("rootNotDeleted")
        
        obj_ids.clear()
        for item in organization_list:
            obj_ids.append(item.id)    
        
        
        retVal = await super().delete_by_ids(obj_ids, tenant_id)
        return retVal == len(obj_ids)    
    
    
    # Client'ın Id bilgisine göre organization listesini döner.
    # Eğer bağlandığı organizationlar'ın (organization_client.is_hierarchical) hiyerarşik bilgisi True olarak işaretlendi ise alt organizationları da bulunur.
    # Second Party ve Third Party uygulamalar için kullanılacaktır.
    async def get_hierarchical_organization_by_client_id(self, client_id: str, user_id:str, tenant_id: str = None) -> List[Organization]:  # type: ignore
        organizations: List[Organization] = []
        try:
            query_args_organization_client: QueryArgs = QueryArgs(
                    where=[
                        Filter(field="client.client_id", op=FilterOp.EQUAL, value=client_id),
                        Filter(field="client.tenant_client.tenant_id", op=FilterOp.EQUAL,value=tenant_id),
                        Filter(field="organization.users.id", op=FilterOp.EQUAL,value=user_id)
                        ],
                    select=[
                        "id","organization_id","client_id","is_hierarchical",
                        "organization.id","organization.name","organization.description","organization.parent_id","organization.is_root","organization.integration_id",
                        "organization.organization_type_id","organization.is_hierarchical","organization.geo",
                        "client.name", "client.client_id", "client.client_secret", "client.grant_types", "client.application_type",
                        ],
                    limit=0,
                    offset=0
                )
            organization_clients: List[OrganizationClient] = await self.organization_client_service.find(query_args_organization_client, tenant_id)
            for organization_client in organization_clients:
                if organization_client.organization is not None:
                    orgData = Organization(**organization_client.organization)
                    if any(item.id == orgData.id for item in organizations) is False:
                        organizations.append(orgData)
                    # Organization_Client a bağlı organization hiyerarşik ise child organizationları da listeye dahil edilir.                                    
                    if organization_client.is_hierarchical:
                        await self.get_hierarchical_child_organization(str(organization_client.organization_id), organizations, tenant_id)
            
            # client ile ilişkisinde ki hiyerarşik bilgisi eklenir.
            for organization in organizations:
                query_args_client: QueryArgs = QueryArgs(
                    where=[
                        Filter(field="organization_id", op=FilterOp.EQUAL,value=organization.id),
                        Filter(field="client_id", op=FilterOp.EQUAL,value=client_id)
                        ],
                    select=[
                        "id","organization_id","client_id","is_hierarchical",
                        ],
                    limit=0,
                    offset=0
                )
                org_client: List[OrganizationClient] = await self.organization_client_service.find(query_args_client,tenant_id)
                if org_client is not None and len(org_client) == 1:
                    organization.client_hierarchical = org_client[0].is_hierarchical     

            return organizations
        except:
            return []
        
    # Organization id bilgisine göre child organizationları bulur 
    async def get_hierarchical_child_organization(self, organization_id:str, organizations:List[Organization], tenant_id: str | None = None)->List[Organization]:
        try:
            query_args_child: QueryArgs = QueryArgs(
                where=[
                    Filter(field="parent_id", op=FilterOp.EQUAL, value=organization_id)  
                ],
                select=[
                        "id","name","description","parent_id","is_root","integration_id","organization_type_id","is_hierarchical","geo",
                    ],
                limit=0,
                offset=0
            )
            child_organization = await super().find(query_args_child, tenant_id)
            for child in child_organization:
                if any(item.id == child.id for item in organizations) is False:
                    organizations.append(child)
                await self.get_hierarchical_child_organization(str(child.id), organizations, tenant_id)
                
            return organizations
        except:
            return organizations
        
        
    # Organization id bilgisine göre parent organizationları bulur 
    async def get_hierarchical_parent_organization(self, organization_parent_id:str, organizations:List[Organization], tenant_id: str | None = None)->List[Organization]:
        try:
            query_args_child: QueryArgs = QueryArgs(
                where=[
                    Filter(field="id", op=FilterOp.EQUAL, value=organization_parent_id)  
                ],
                select=[
                        "id","name","description","parent_id","is_root","integration_id","organization_type_id","is_hierarchical","geo",
                    ],
                limit=0,
                offset=0
            )
            parent_organization = await super().find(query_args_child, tenant_id)
            for parent in parent_organization:
                if any(item.id == parent.id for item in organizations) is False:
                    organizations.append(parent)
                await self.get_hierarchical_parent_organization(str(parent.parent_id), organizations, tenant_id)
                
            return organizations
        except:
            return organizations