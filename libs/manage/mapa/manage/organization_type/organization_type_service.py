from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType, OrganizationType, UpdateAllOrganizationType, UpdateOrganizationType
from mapa.manage.organization_type.organization_type_repository import OrganizationTypeRepository
from uuid import UUID
from typing import Any,List

class OrganizationTypeService(BaseEntityService[OrganizationTypeRepository, OrganizationType, CreateOrganizationType, UpdateOrganizationType, UpdateAllOrganizationType]):
    """OrganizationTypeService""" 

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationTypeRepository, OrganizationType)

    # sorgulama işlemi yapıldığında bulunan kayıtların parent bilgileride bulunmaktadır.
    async def paging(self, query_args: QueryArgs, tenant_id: str | None = None) -> PagingResult[OrganizationType]:
        organization_type_list = []
        result = await super().paging(query_args, tenant_id)

        if result and len(result.items) > 0:
            for organization_type in result.items:
                if any(item.id == organization_type.id for item in organization_type_list) is False:
                    organization_type_list.append(organization_type)
                await self.get_hierarchical_parent_organization_type(str(organization_type.parent_id), organization_type_list, tenant_id) 
            result.items = organization_type_list
            result.total = len(organization_type_list)
        return result    


    # Organization Type bilgisinde root kaydın silinmemesi için kontrol eklendi.
    # Silinmek istenen Organization Type'ın childları da listeye dahil edildi.
    async def delete_by_ids(self, obj_ids: List[Any], tenant_id: str | None = None) -> int:
        organization_type_list = []
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.IN, value=obj_ids),
        ], limit=0, offset=0)
        organization_types = await super().paging(query_args, tenant_id)
        
        if organization_types is not None and len(organization_types.items) > 0:
            for organization_type in organization_types.items:
                organization_type_list.append(organization_type) 
                await self.get_hierarchical_child_organization_type(str(organization_type.id), organization_type_list, tenant_id)
        
        filtered_list = [item for item in organization_type_list if item.is_root == True]
        if len(filtered_list) > 0:
            raise ValueError("rootNotDeleted")
        
        obj_ids.clear()
        for item in organization_type_list:
            obj_ids.append(item.id)   
            
        return await super().delete_by_ids(obj_ids, tenant_id)

    # Organization Type bilgisinde root kaydın silinmemesi için kontrol eklendi.
    # Silinmek istenen Organization Type'ın childları da listeye dahil edildi.
    async def delete_all(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        organization_type_list = []
        query_args.offset = 0
        query_args.limit = 0
        organization_types = await super().paging(query_args, tenant_id)
        
        if organization_types is not None and len(organization_types.items) > 0:
            for organization_type in organization_types.items:
                organization_type_list.append(organization_type) 
                await self.get_hierarchical_child_organization_type(str(organization_type.id), organization_type_list, tenant_id)
        
        filtered_list = [item for item in organization_type_list if item.is_root == True]
        if len(filtered_list) > 0:
            raise ValueError("rootNotDeleted")
        
        if query_args.where is None or len(query_args.where)==0:
            query_args.where = []
            
        for filter in query_args.where:
            if filter and filter.model_dump().get("field") == "id":
                filter.value = [item.id for item in organization_type_list]
        
        return await super().delete_all(query_args, tenant_id)

    # Organization Type bilgisinde root kaydın silinmemesi için kontrol eklendi.
    # Silinmek istenen Organization Type'ın childları da listeye dahil edildi.
    async def delete(self, obj_id: Any, tenant_id: str | None = None) -> bool:
        organization_type_list = []
        obj_ids=[]
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=obj_id),
        ], limit=0, offset=0)
        organization_types = await super().paging(query_args, tenant_id)
        
        if organization_types is not None and len(organization_types.items) > 0:
            for organization in organization_types.items:
                organization_type_list.append(organization) 
                await self.get_hierarchical_child_organization_type(str(organization.id), organization_type_list, tenant_id)
        
        filtered_list = [item for item in organization_type_list if item.is_root == True]
        if len(filtered_list) > 0:
            raise ValueError("rootNotDeleted")
        
        obj_ids.clear()
        for item in organization_type_list:
            obj_ids.append(item.id)    
        
        retVal = await super().delete_by_ids(obj_ids, tenant_id)
        return retVal == len(obj_ids)
    
    
    # Organization Type id bilgisine göre child organization typeları bulur 
    async def get_hierarchical_child_organization_type(self, organization_type_id:str, organization_types:List[OrganizationType], tenant_id: str | None = None)->List[OrganizationType]:
        try:
            query_args_child: QueryArgs = QueryArgs(
                where=[
                    Filter(field="parent_id", op=FilterOp.EQUAL, value=organization_type_id)  
                ],
                select=[
                        "id","name","description","parent_id","is_root",
                    ],
                limit=0,
                offset=0
            )
            child_organization_type = await super().find(query_args_child, tenant_id)
            for child in child_organization_type:
                organization_types.append(child)
                await self.get_hierarchical_child_organization_type(str(child.id), organization_types, tenant_id)
                
            return organization_types
        except:
            return organization_types
        
    # Organization Type id bilgisine göre parent organization typeları bulur 
    async def get_hierarchical_parent_organization_type(self, organization_type_parent_id:str, organization_types:List[OrganizationType], tenant_id: str | None = None)->List[OrganizationType]:
        try:
            query_args_child: QueryArgs = QueryArgs(
                where=[
                    Filter(field="id", op=FilterOp.EQUAL, value=organization_type_parent_id)  
                ],
                select=[
                        "id","name","description","parent_id","is_root",
                    ],
                limit=0,
                offset=0
            )
            parent_organization_type = await super().find(query_args_child, tenant_id)
            for parent in parent_organization_type:
                if any(item.id == parent.id for item in organization_types) is False:
                    organization_types.append(parent)
                await self.get_hierarchical_parent_organization_type(str(parent.parent_id), organization_types, tenant_id)
                
            return organization_types
        except:
            return organization_types