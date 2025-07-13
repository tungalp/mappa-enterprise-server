from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser, OrganizationUser, UpdateAllOrganizationUser, UpdateOrganizationUser
from mapa.manage.organization_user.organization_user_repository import OrganizationUserRepository
from uuid import UUID


class OrganizationUserService(BaseEntityService[OrganizationUserRepository, OrganizationUser, CreateOrganizationUser, UpdateOrganizationUser, UpdateAllOrganizationUser]):
    """OrganizationUserService""" 

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationUserRepository, OrganizationUser)
