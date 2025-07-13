from typing import Any, List
from uuid import UUID
from bcrypt import hashpw, gensalt, checkpw
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.result import PagingResult
from mapa.manage.api_scope.api_scope_model import ApiScope
from mapa.manage.invitation.invitation_service import InvitationService
from mapa.manage.organization.organization_model import Organization
from mapa.manage.organization_client.organization_client_model import OrganizationClient
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser, User
from mapa.manage.user.user_repository import UserRepository
from mapa.manage.api.api_service import ApiService
from mapa.manage.organization.organization_service import OrganizationService


class UserService(
    BaseEntityService[UserRepository, User, CreateUser, UpdateUser, UpdateAllUser]
):
    """User Servisi"""

    def __init__(
        self,
        async_db: AsyncDatabase,
        api_service: ApiService,
        organization_service: OrganizationService,
    ) -> None:
        super().__init__(async_db, UserRepository, User)
        self.api_service = api_service
        self.organization_service = organization_service

    async def get_by_user_id(self, user_id: UUID, tenant_id: str = None, fields: list[str] = []) -> User:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(user_id, tenant_id, fields)

    async def get_by_email(self, email: str, tenant_id: str | None = None) -> User | None:
        """Email adresine göre kullanıcı getirir"""

        return await self.find_one(
            QueryArgs(where=[Filter(field="email", op=FilterOp.EQUAL, value=email)]), tenant_id
        )

    async def create(self, input_obj: CreateUser, tenant_id: str | None = None) -> User:
        """Kullanıcıyı oluştururken şifreyi hashleyerek kaydeder."""

        encoding = "utf-8"
        input_obj.password = hashpw(
            input_obj.password.encode(encoding), gensalt()
        ).decode(encoding)

        return await super().create(input_obj, tenant_id)

    async def create_all(
        self,
        input_objs: List[CreateUser],
        tenant_id: str | None = None,
        hash_password: bool = True,
    ) -> List[User]:
        """Kullanıcıları oluştururken hash_password true ise şifreyi hashleyerek kaydeder."""
        if hash_password:
            for input_obj in input_objs:
                encoding = "utf-8"
                input_obj.password = hashpw(
                    input_obj.password.encode(encoding), gensalt()
                ).decode(encoding)

        return await super().create_all(input_objs, tenant_id)

    async def check_password(self, user_id: UUID, password: str) -> bool:
        """Kullanıcının şifresinin doğru olup olmadığını kontrol eder."""

        encoding = "utf-8"
        user = await self.repo.get(user_id)
        return checkpw(password.encode(encoding), user.password.encode(encoding))

    async def update_password(self, user_id: UUID, password: str) -> User:
        """Kullanıcının şifresini günceller"""

        encoding = "utf-8"
        new_password = hashpw(password.encode(encoding), gensalt()).decode(encoding)
        updated_user = UpdateUser(password=new_password)
        return await self.update(user_id, updated_user)  # type: ignore

    async def delete_all(
        self, query_args: QueryArgs, tenant_id: str | None = None
    ) -> int:
        """Gelen query_args parametresi ile eşleşen kayıtları siler."""
        query_args.offset = 0
        query_args.limit = 0
        if query_args.where == None:
            query_args.where = []
        query_args.where.append(
            Filter(field="tenant_users.tenant_id", op=FilterOp.EQUAL, value=tenant_id)
        )
        query_args.where.append(
            Filter(field="tenant_users.role", op=FilterOp.NOT_EQUAL, value="owner")
        )
        return await super().delete_all(query_args, tenant_id)

    async def count(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Gelen query_args parametresi ile eşleşen kayıtların sayısını döner."""
        if query_args.where == None:
            query_args.where = []
        query_args.where.append(
            Filter(field="tenant_users.tenant_id", op=FilterOp.EQUAL, value=tenant_id)
        )
        query_args.where.append(
            Filter(field="tenant_users.role", op=FilterOp.NOT_EQUAL, value="owner")
        )
        return await super().count(query_args, tenant_id)

    async def paging(
        self, query_args: QueryArgs, tenant_id: str | None = None
    ) -> PagingResult[User]:
        """Sorgu parametrelerine uyan kayıtları PagingResult sayfa sonuç değeri olarak döndürür."""
        if query_args.where == None:
            query_args.where = []
        query_args.where.append(
            Filter(field="tenant_users.tenant_id", op=FilterOp.EQUAL, value=tenant_id)
        )
        query_args.where.append(
            Filter(field="tenant_users.role", op=FilterOp.NOT_EQUAL, value="owner")
        )
        return await super().paging(query_args, tenant_id)  # type: ignore

    async def get_user_scopes(
        self, client_id: str, user_id: str, tenant_id: str | None = None
    ) -> List[str]:
        """Sorgu parametrelerine uyan kayıtların scope listesini List[str] sonuç değeri olarak döndürür."""
        query_args: QueryArgs
        user_scopes: List[str] = []
        try:
            query_args = QueryArgs(
                where=[
                    Filter(
                        field="tenant_users.user_id", op=FilterOp.EQUAL, value=user_id
                    ),
                    Filter(
                        field="tenant_users.tenant_id",
                        op=FilterOp.EQUAL,
                        value=tenant_id,
                    ),
                ],
                select=[
                    "id",
                    "name",
                    "surname",
                    "email",
                    "password",
                    "email_verified",
                    "phone",
                    "subject_id",
                    "context",
                    "created_at",
                    "tenant_users.id",
                    "tenant_users.user_id",
                    "tenant_users.tenant_id",
                    "tenant_users.role",
                ],
                limit=0,
                offset=0,
            )
            users = await super().find(query_args, tenant_id)  # type: ignore
            if (
                users is not None
                and len(users) == 1
                and users[0].tenant_users is not None
                and users[0].tenant_users is not None
                and users[0].tenant_users[0]["role"] == "owner"
            ):
                query_args = QueryArgs(
                    where=[
                        Filter(
                            field="client_api.client_id",
                            op=FilterOp.EQUAL,
                            value=client_id,
                        ),
                    ],
                    select=[
                        "id",
                        "name",
                        "identifier",
                        "allow_offline_access",
                        "skip_consent_for_verifiable_first_party_clients",
                        "token_lifetime",
                        "token_lifetime_for_web",
                        "signing_alg",
                        "is_system",
                        "client_api.api_id",
                        "client_api.client_id",
                        "api_scopes.id",
                        "api_scopes.name",
                        "api_scopes.description",
                        "api_scopes.api_id",
                    ],
                    limit=0,
                    offset=0,
                )
                apis = await self.api_service.paging(query_args, tenant_id)
                for api in apis.items:
                    if api.api_scopes is not None and len(api.api_scopes) > 0:
                        for api_scope in api.api_scopes:
                            user_scopes.append(api_scope.name)
            else:
                query_args = QueryArgs(
                    where=[
                        Filter(
                            field="roles.users.id", op=FilterOp.EQUAL, value=user_id
                        ),
                        Filter(
                            field="roles.api_scopes.api.client_api.client_id",
                            op=FilterOp.EQUAL,
                            value=client_id,
                        ),
                    ],
                    select=[
                        "id",
                        "name",
                        "surname",
                        "email",
                        "password",
                        "email_verified",
                        "phone",
                        "context",
                        "subject_id",
                        "created_at",
                        "roles.id",
                        "roles.name",
                        "roles.description",
                        "roles.api_scopes.name",
                        "roles.api_scopes.description",
                        "roles.api_scopes.name",
                        "roles.api_scopes.api.name",
                        "roles.api_scopes.api.id",
                        "roles.api_scopes.api.identifier",
                        "roles.api_scopes.api.client_api.api_id",
                        "roles.api_scopes.api.client_api.client_id",
                    ],
                    limit=0,
                    offset=0,
                )
                users = await super().find(query_args, tenant_id)  # type: ignore

                if (
                    users is not None
                    and len(users) == 1
                    and users[0].roles is not None
                    and len(users[0].roles) > 0
                ):
                    for role in users[0].roles:
                        if (
                            role["api_scopes"] is not None
                            and len(role["api_scopes"]) > 0
                        ):
                            for api_scope in role["api_scopes"]:
                                user_scopes.append(api_scope["name"])

            # Organizationdan gelen scopeları bulmak için eklenmiştir. (1.03.2024)
            query_args_organization: QueryArgs = QueryArgs(
                where=[
                    Filter(field="id", op=FilterOp.EQUAL, value=user_id),
                ],
                select=[
                    "id",
                    "name",
                    "surname",
                    "email",
                    "password",
                    "email_verified",
                    "phone",
                    "subject_id",
                    "context",
                    "created_at",
                    "organizations.id",
                    "organizations.name",
                    "organizations.description",
                    "organizations.parent_id",
                    "organizations.is_root",
                    "organizations.integration_id",
                    "organizations.organization_type_id",
                    "organizations.is_hierarchical",
                    "organizations.roles.id",
                    "organizations.roles.name",
                    "organizations.roles.description",
                    "organizations.roles.api_scopes.name",
                    "organizations.roles.api_scopes.description",
                    "organizations.roles.api_scopes.api_id",
                ],
                limit=0,
                offset=0,
            )

            organization_list = await super().find(query_args_organization, tenant_id)
            if (
                organization_list is not None
                and len(organization_list) == 1
                and organization_list[0].organizations is not None
                and len(organization_list[0].organizations) > 0
            ):
                for organization in organization_list[0].organizations:
                    # Mevcut scopelar
                    if (
                        organization["roles"] is not None
                        and len(organization["roles"]) > 0
                    ):
                        for role in organization["roles"]:
                            if (
                                role["api_scopes"] is not None
                                and len(role["api_scopes"]) > 0
                            ):
                                for api_scope in role["api_scopes"]:
                                    user_scopes.append(api_scope["name"])
                    # Organization hiyerarşik ise child organizationların da scopeları dahil edilir.
                    if organization["is_hierarchical"]:
                        await self.get_user_scope_child_organization(
                            str(organization["id"]), user_scopes, tenant_id
                        )
            # end of Organizationdan gelen scopeları bulmak için eklenmiştir. (1.03.2024)

            user_scopes = list(set(user_scopes))
            return user_scopes
        except:
            user_scopes = list(set(user_scopes))
            return user_scopes

    # Organization id bilgisine göre child organizationları bulur ve onların scope'larını da listeye ekler.
    async def get_user_scope_child_organization(
        self, organization_id: str, user_scopes: List[str], tenant_id: str | None = None
    ) -> List[str]:
        try:
            query_args_child: QueryArgs = QueryArgs(
                where=[
                    Filter(field="parent_id", op=FilterOp.EQUAL, value=organization_id)
                ],
                select=[
                    "id",
                    "name",
                    "description",
                    "parent_id",
                    "is_root",
                    "integration_id",
                    "organization_type_id",
                    "is_hierarchical",
                    "roles.id",
                    "roles.name",
                    "roles.description",
                    "roles.api_scopes.name",
                    "roles.api_scopes.description",
                    "roles.api_scopes.api_id",
                ],
                limit=0,
                offset=0,
            )
            child_organization = await self.organization_service.find(
                query_args_child, tenant_id
            )
            for child in child_organization:
                if child.roles is not None and len(child.roles) > 0:
                    for role in child.roles:
                        if (
                            role["api_scopes"] is not None
                            and len(role["api_scopes"]) > 0
                        ):
                            for api_scope in role["api_scopes"]:
                                user_scopes.append(api_scope["name"])

                await self.get_user_scope_child_organization(
                    str(child.id), user_scopes, tenant_id
                )

            return user_scopes
        except:
            return user_scopes

    # Client'ın Id bilgisine göre organization listesini döner.
    # Eğer bağlandığı organizationlar'ın (organization_client.is_hierarchical) hiyerarşik bilgisi True olarak işaretlendi ise alt organizationları da bulunur.
    # Second Party ve Third Party uygulamalar için kullanılacaktır.
    async def get_hierarchical_organization_by_client_id(self, client_id: str, user_id: str, tenant_id: str = None) -> List[Organization]:  # type: ignore
        organizations: List[Organization] = []
        try:
            query_args_organization_client: QueryArgs = QueryArgs(
                where=[
                    Filter(
                        field="client.client_id", op=FilterOp.EQUAL, value=client_id
                    ),
                    Filter(
                        field="client.tenant_client.tenant_id",
                        op=FilterOp.EQUAL,
                        value=tenant_id,
                    ),
                    Filter(
                        field="organization.users.id", op=FilterOp.EQUAL, value=user_id
                    ),
                ],
                select=[
                    "id",
                    "organization_id",
                    "client_id",
                    "is_hierarchical",
                    "organization.id",
                    "organization.name",
                    "organization.description",
                    "organization.parent_id",
                    "organization.is_root",
                    "organization.integration_id",
                    "organization.organization_type_id",
                    "organization.is_hierarchical",
                    "organization.geo",
                    "client.name",
                    "client.client_id",
                    "client.client_secret",
                    "client.grant_types",
                    "client.application_type",
                ],
                limit=0,
                offset=0,
            )
            organization_clients: List[OrganizationClient] = (
                await self.organization_service.organization_client_service.find(
                    query_args_organization_client, tenant_id
                )
            )
            for organization_client in organization_clients:
                if organization_client.organization is not None:
                    orgData = Organization(**organization_client.organization)
                    if any(item.id == orgData.id for item in organizations) is False:
                        organizations.append(orgData)
                    # Organization_Client a bağlı organization hiyerarşik ise child organizationları da listeye dahil edilir.
                    if organization_client.is_hierarchical:
                        await self.organization_service.get_hierarchical_child_organization(
                            str(organization_client.organization_id),
                            organizations,
                            tenant_id,
                        )

            # client ile ilişkisinde ki hiyerarşik bilgisi eklenir.
            for organization in organizations:
                query_args_client: QueryArgs = QueryArgs(
                    where=[
                        Filter(
                            field="organization_id",
                            op=FilterOp.EQUAL,
                            value=organization.id,
                        ),
                        Filter(field="client_id", op=FilterOp.EQUAL, value=client_id),
                    ],
                    select=[
                        "id",
                        "organization_id",
                        "client_id",
                        "is_hierarchical",
                    ],
                    limit=0,
                    offset=0,
                )
                org_client: List[OrganizationClient] = (
                    await self.organization_service.organization_client_service.find(
                        query_args_client, tenant_id
                    )
                )
                if org_client is not None and len(org_client) == 1:
                    organization.client_hierarchical = org_client[0].is_hierarchical

            return organizations
        except:
            return []
