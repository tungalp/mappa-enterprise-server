import asyncio
from datetime import datetime
from typing import Any, List, Set
from cryptography.fernet import Fernet
from ldap3 import Server, Connection
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from mapa.manage.client.client_service import ClientService
from mapa.manage.ldap_server.ldap_server_model import (
    CreateLdapServer,
    LdapServer,
    LdapUser,
    UpdateAllLdapServer,
    UpdateLdapServer,
)
from mapa.manage.ldap_server.ldap_server_repository import LdapServerRepository
from uuid import UUID
import base64

from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization_type.organization_type_service import (
    OrganizationTypeService,
)
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser
from mapa.manage.organization_user.organization_user_service import (
    OrganizationUserService,
)
from mapa.manage.tenant.tenant_model import CreateTenant
from mapa.manage.tenant.tenant_service import TenantService
from mapa.manage.tenant_user.tenant_user_model import CreateTenantUser, TenantUserRole
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.manage.user.user_model import CreateUser, UpdateUser, User
from mapa.manage.user.user_service import UserService
from nanoid import generate


class LdapServerService(
    BaseEntityService[
        LdapServerRepository,
        LdapServer,
        CreateLdapServer,
        UpdateLdapServer,
        UpdateAllLdapServer,
    ]
):
    """LdapServerService"""

    def __init__(
        self,
        async_db: AsyncDatabase,
        user_service: UserService,
        client_service: ClientService,
        tenant_service: TenantService,
        tenant_user_service: TenantUserService,
        organization_service: OrganizationService,
        organization_type_service: OrganizationTypeService,
        organization_user_service: OrganizationUserService,
    ) -> None:
        super().__init__(async_db, LdapServerRepository, LdapServer)
        self._key = "SeT-qFS5AbjCe1ObXn5XDZUp7b_otdDUiGKhm2fWKHM="
        self._user_service = user_service
        self._client_service = client_service
        self._tenant_service = tenant_service
        self._tenant_user_service = tenant_user_service
        self._organization_type_service = organization_type_service
        self._organization_service = organization_service
        self._organization_user_service = organization_user_service

    async def create(
        self, input_obj: CreateLdapServer, tenant_id: str | None = None
    ) -> LdapServer:
        """Kullanıcıyı oluştururken şifreyi hashleyerek kaydeder."""

        encoding = "utf-8"
        input_obj.password = self.encrypt_data(
            input_obj.password, self._key.encode(encoding=encoding)
        )
        return await super().create(input_obj, tenant_id)

    async def create_all(
        self, input_objs: List[CreateLdapServer], tenant_id: str | None = None
    ) -> List[LdapServer]:
        """Kullanıcıları oluştururken şifreyi kriptolayarak kaydeder."""
        for input_obj in input_objs:
            encoding = "utf-8"
            input_obj.password = self.encrypt_data(
                input_obj.password, self._key.encode(encoding=encoding)
            )

        return await super().create_all(input_objs, tenant_id)

    async def update(
        self,
        ldap_server_id: Any,
        input_obj: UpdateLdapServer,
        tenant_id: str | None = None,
    ) -> LdapServer:
        """Kullanıcıyı güncellerken şifreyi kriptolayarak kaydeder."""

        encoding = "utf-8"
        input_obj.password = self.encrypt_data(input_obj.password, self._key.encode(encoding=encoding))  # type: ignore
        return await super().update(ldap_server_id, input_obj, tenant_id)  # type: ignore

    async def check_ldap_connection_with_mail_password(
        self,
        ldap_server_id: str | None = None,
        mail: str | None = None,
        password: str | None = None,
    ) -> bool:
        """Ldap bağlantısını kontrol eder."""
        is_connected = False
        ldap_server = await super().get(ldap_server_id)
        try:
            server = Server(ldap_server.url, get_info=ldap_server.get_info)  # type: ignore
            connection = Connection(server, user=mail, password=password, authentication=ldap_server.authentication, auto_bind=ldap_server.auto_bind)  # type: ignore
            if connection.bound:
                is_connected = True
        except Exception as e:
            print(f"LDAP bağlantısı sırasında hata oluştu: {e}")
            is_connected = False
        finally:
            if "connection" in locals() and connection.bound:
                connection.unbind()

        return is_connected

    async def check_ldap_connection(
        self, ldap_server_id: str | None = None, tenant_id: str | None = None
    ) -> bool:
        """Ldap bağlantısını kontrol eder."""
        is_connected = False
        ldap_server = await super().get(ldap_server_id, tenant_id)
        encoding = "utf-8"
        ldap_server.password = self.decrypt_data(
            ldap_server.password, self._key.encode(encoding=encoding)  # type: ignore
        )
        try:
            server = Server(ldap_server.url, get_info=ldap_server.get_info)  # type: ignore
            connection = Connection(server, user=ldap_server.username, password=ldap_server.password, authentication=ldap_server.authentication, auto_bind=ldap_server.auto_bind)  # type: ignore
            if connection.bound:
                is_connected = True
        except Exception as e:
            print(f"LDAP bağlantısı sırasında hata oluştu: {e}")
            is_connected = False
        finally:
            if "connection" in locals() and connection.bound:
                connection.unbind()

        return is_connected

    async def start_sync(
        self, ldap_server_id: str, tenant_id: str | None = None
    ) -> bool:
        ldap_server = await super().get(ldap_server_id, tenant_id)
        encoding = "utf-8"
        ldap_server.password = self.decrypt_data(ldap_server.password, self._key.encode(encoding=encoding))  # type: ignore

        try:
            server = Server(ldap_server.url, get_info=ldap_server.get_info)  # type: ignore
            connection = Connection(
                server,
                user=ldap_server.username,
                password=ldap_server.password,
                authentication=ldap_server.authentication,  # type: ignore
                auto_bind=ldap_server.auto_bind,  # type: ignore
            )

            if not connection.bound:
                raise ConnectionError("LDAP connection could not be established.")

            attributes = [
                attr
                for _, attr_list in ldap_server.attribute_map.items()
                for attr in attr_list
            ]
            connection.search(
                search_base=ldap_server.search_base,
                search_filter=ldap_server.search_filter,
                attributes=attributes,
            )

            ldap_users: List[LdapUser] = []
            ldap_emails: Set[str] = set()

            # LDAP Kullanıcılarını Al
            for entry in connection.entries:
                user_data = {
                    key: (
                        getattr(entry, attr).value
                        if hasattr(entry, attr) and getattr(entry, attr).value
                        else ""
                    )
                    for key, attr_list in ldap_server.attribute_map.items()
                    for attr in attr_list
                }

                is_active = (
                    not bool(int(entry.userAccountControl.value) & 0x0002)
                    if "userAccountControl" in entry
                    else False
                )

                email = user_data["email"].lower()
                ldap_emails.add(email)
                if email != "":
                    ldap_users.append(
                        LdapUser(
                            name=user_data.get("firstname", ""),
                            middlename=user_data.get("middlename", ""),
                            surname=user_data.get("lastname", ""),
                            email=email,
                            phone=user_data.get("phone", "").replace(" ", ""),
                            password="LdapUserNullPassword",
                            is_active=is_active,
                            ldap_user_id=UUID(ldap_server_id),
                        )
                    )

            query_args = QueryArgs(
                where=[
                    Filter(
                        field="ldap_server_id",
                        op=FilterOp.EQUAL,
                        value=ldap_server_id,
                    )
                ],
                offset=0,
                limit=0,
            )

            existing_users = {
                user.email: user for user in await self._user_service.find(query_args)
            }

            new_users = [
                CreateUser(
                    name=ldap_user.name
                    + (" " + ldap_user.middlename if ldap_user.middlename else ""),
                    surname=ldap_user.surname,
                    email=ldap_user.email,
                    password=ldap_user.password,
                    phone=ldap_user.phone,
                    email_verified=True,
                    is_ldap_user=True,
                    ldap_server_id=ldap_user.ldap_user_id,
                    blocked=not ldap_user.is_active,
                )
                for ldap_user in ldap_users
                if ldap_user.email not in existing_users
            ]

            if new_users:
                created_users = await self._user_service.create_all(
                    new_users, tenant_id, False
                )
                create_tenant_for_users = []
                for new_user in created_users:                    
                    create_tenant_for_users.append(self.create_tenant_for_user(new_user, tenant_id))
                if create_tenant_for_users:
                    await asyncio.gather(*create_tenant_for_users)

            update_tasks = []
            for ldap_user in ldap_users:
                existing_user = existing_users.get(ldap_user.email)

                if existing_user:
                    full_name = ldap_user.name + (
                        " " + ldap_user.middlename if ldap_user.middlename else ""
                    )

                    if (
                        existing_user.name != full_name
                        or existing_user.surname != ldap_user.surname
                        or existing_user.phone != ldap_user.phone
                        or existing_user.blocked != (not ldap_user.is_active)
                    ):
                        update_tasks.append(
                            self._user_service.update(
                                existing_user.id,
                                UpdateUser(
                                    name=ldap_user.name
                                    + (
                                        " " + ldap_user.middlename
                                        if ldap_user.middlename
                                        else ""
                                    ),
                                    surname=ldap_user.surname,
                                    phone=ldap_user.phone,
                                    blocked=not ldap_user.is_active,
                                ),
                            )
                        )

            if update_tasks:
                await asyncio.gather(*update_tasks)

            users_to_disable = [
                user
                for user in existing_users.values()
                if user.email not in ldap_emails
            ]

            if users_to_disable:
                disable_tasks = [
                    self._user_service.update(user.id, UpdateUser(blocked=True))
                    for user in users_to_disable
                ]
                await asyncio.gather(*disable_tasks)

            return True
        except Exception as e:
            print(f"Error during LDAP sync: {e}")
            return False

    async def create_tenant_for_user(self, user, tenant_id: str | None = None):
        email_parts = user.email.split("@")
        tenant_name = f"{email_parts[0]}-{email_parts[1].split('.')[0]}"
        queryArgs = QueryArgs(
            where=[
                Filter(field="name", op=FilterOp.EQUAL, value=tenant_name),
            ]
        )
        if await self._tenant_service.count(queryArgs) != 0:
            tenant_name += "-" + generate(
                alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                size=6,
            )

        tenant_title = " ".join([user.name, user.surname])
        tenant = await self._tenant_service.create(
            CreateTenant(name=tenant_name, user_id=user.id, title=tenant_title)
        )

        await self._tenant_user_service.create(
            CreateTenantUser(
                user_id=user.id, tenant_id=tenant.id, role=TenantUserRole.OWNER
            ),
            tenant_id=str(tenant.id),
        )

        await self._tenant_user_service.create(
            CreateTenantUser(
                user_id=user.id, tenant_id=UUID(tenant_id), role=TenantUserRole.MEMBER
            ),
            tenant_id=tenant_id,
        )  # NOT : Ldap Server'ın bağlı olduğu tenant_id kullanılmıştır.

        organization_type = await self._organization_type_service.create(
            CreateOrganizationType(
                name=tenant_name,
                description=tenant_name,
                is_root=True,
            ),
            tenant_id=str(tenant.id),
        )

        organization = await self._organization_service.create(
            CreateOrganization(
                name=tenant_name,
                description=tenant_name,
                is_root=True,
                organization_type_id=organization_type.id,
                is_hierarchical=True,
            ),
            tenant_id=str(tenant.id),
        )

        await self._organization_user_service.create(
            CreateOrganizationUser(user_id=user.id, organization_id=organization.id),
            tenant_id=str(tenant.id),
        )

        return tenant

    def encrypt_data(self, data: str, key: bytes) -> str:
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str, key: bytes) -> str:
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes).decode()
        return decrypted_data
