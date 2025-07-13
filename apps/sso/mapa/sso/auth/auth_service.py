from datetime import datetime, timedelta
from typing import Any, Tuple
from uuid import UUID, uuid4
from nanoid import generate
import jwt
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.core.data.base_service import BaseService
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.auth.new_password_endpoint import NewPasswordEndpoint
from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.sso.consent.consent_model import Consent, CreateConsent, UpdateConsent
from mapa.sso.consent.consent_service import ConsentService
from mapa.sso.oidc.validation.authorize_endpoint_validator import (
    AuthorizeEndPointValidator,
)
from mapa.sso.oidc.validation.authorize_request import AuthorizeRequest
from mapa.sso.user_session.user_session_model import (
    CreateUserSession,
    UpdateUserSession,
    UserSession,
)
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.user_session_client.user_session_client_model import (
    CreateUserSessionClient,
)
from mapa.sso.user_session_client.user_session_client_service import (
    UserSessionClientService,
)
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs

from mapa.sso.models import (
    CreateTenant,
    CreateTenantUser,
    CreateOrganization,
    CreateOrganizationType,
    CreateOrganizationUser,
    CreateUser,
    TenantUser,
    TenantUserRole,
    UpdateInvitation,
    User
)
class AuthService(BaseService):
    """Kimliklendirme servisi. Kullanıcı kimlik kontrolü ve yeni kayıt işlemlerini yapar"""

    def __init__(
        self,
        jwt_secret: str,
        session_timeout: int,
        authorize_validator: AuthorizeEndPointValidator,
        user_session_service: UserSessionService,
        user_session_client_service: UserSessionClientService,
        consent_service: ConsentService,
        messenger: ServiceMessenger
    ) -> None:
        self._jwt_secret = jwt_secret
        self._session_timeout = session_timeout
        self._authorize_validator = authorize_validator
        self._user_session_service = user_session_service
        self._user_session_client_service = user_session_client_service
        self._consent_service = consent_service
        self._messenger = messenger
        super().__init__()

    async def login(
        self, session_id: UUID, login_endpoint: LoginEndpoint
    ) -> Tuple[UUID, UserSession, AuthorizeRequest]:
        """Kullanıcının kimlik kontrolünü yapar ve olumlu ise kullanıcı için oturum açar ya da
        varolan oturum bilgilerini günceller.
        Dönüş değeri olarak kullanıcı oturumu ve kontrol edilmiş istek döndürülür"""

        # Gelen istek kontrol edilir
        val_result = await self._authorize_validator.validate(
            login_endpoint, session_id
        )
        if val_result.error:
            raise ValueError(val_result.error)
        auth_request: AuthorizeRequest = val_result.result

        # Eğer mevcut bir session varsa login kısmı pasif hale getirilir. Eğer login işlemi
        # başarılı olursa tekrar aktif hale getirilir.
        if auth_request.user_session:
            await self._user_session_service.update(
                auth_request.user_session.id, UpdateUserSession(authenticated=False)
            )
        #
        user = await self._messenger.user_get_by_email(login_endpoint.email)
        if not user:
            raise ValueError("User not found")
            # raise ValueError(f"{login_endpoint.email} not found")

        # NOT : Kullanıcı engellendi ise giriş yapması engellenir. (19.07.2023)
        if user["blocked"] == True:
            raise ValueError("The user has been blocked")
            # raise ValueError(f"The {user.email} has been blocked.")

        if user["is_ldap_user"] == True:
            is_connected = await self._messenger.check_ldap_connection_with_mail_password(
                str(user["ldap_server_id"]), login_endpoint.email, login_endpoint.password
            )
            if is_connected["success"]:
                try:
                    password_match = await self._messenger.check_password(
                        user["id"], login_endpoint.password
                    )
                except:
                    password_match = False
                if not password_match:
                    await self._messenger.update_password(
                        user["id"], login_endpoint.password
                    )
            else:
                raise ValueError("Password or email does not match")
        else:
            # Şifre kontrol edilir.
            password_match = await self._messenger.check_password(
                user["id"], login_endpoint.password
            )
            if not password_match:
                raise ValueError("Password does not match")
                # raise ValueError(f"{user.email} password doesn't match")

        # Davet varsa kontrol edilir.
        invitation_id = auth_request.invitation
        invitation = (
            await self._get_invitation(invitation_id) if invitation_id else None
        )

        # UserSession daha önceden oluşturulmuşsa o kullanılır yoksa yeni bir usersession oluşturulur.
        user_session = auth_request.user_session
        authenticated_at = datetime.now()
        expired_at = authenticated_at + timedelta(minutes=self._session_timeout)
        user_session_id = session_id if not user_session else uuid4()

        # Eğer session varsa ve bu kullanıcıya aitse güncellenir. Aksi durumda yeni bir session oluşturulur.
        if user_session and user_session.user_id == user["id"]:
            user_session = await self._user_session_service.update(
                user_session.id,
                UpdateUserSession(
                    authenticated_at=authenticated_at,
                    expired_at=expired_at,
                    authenticated=True,
                ),
            )
        else:
            user_session = await self._user_session_service.create(
                CreateUserSession(
                    id=user_session_id,
                    user_id=user["id"],
                    authenticated_at=authenticated_at,
                    expired_at=expired_at,
                    authenticated=True,
                )
            )

        # Eğer davetiye varsa davetiyedeki tenant kullanılarak user_session_client oluşturulur
        # Aksi durumda kullanıcının sahip olduğu tenant ya da tenantlardan biri kullanılır
        if invitation:
            tenant_id = invitation["tenant"]
            # Not : Bu blok mapa > manage > invitation > invitation_util_service altında check_invitation methoduna taşınmıştır. (03.08.2023)
            # queryArgs = QueryArgs(
            #     where=[
            #         Filter(field="tenant_id",
            #                op=FilterOp.EQUAL, value=invitation.tenant),
            #         Filter(field="user_id",
            #                op=FilterOp.EQUAL, value=user["id"])
            #     ]
            # )
            # # NOT : Aynı user 2. kez farklı bir tenant'a davet edildiği zaman ilgili TenantUser bilgisi varmı yokmu kontrol edilir. (19.07.2023)
            # tenant_user_kontrol = await self._tenant_user_service.find(queryArgs, tenant_id=str(invitation.tenant))

            # # NOT : Eğer aynı user 2. kez farklı bir tenant'a devet edilmiş olup ilgili TenantUser bilgisi yoksa TenantUser bilgisi oluşturulur. (19.07.2023)
            # if not tenant_user_kontrol:
            #     guest_user = await self._tenant_user_service.create(CreateTenantUser(
            #         user_id=user["id"],
            #         tenant_id=invitation.tenant,
            #         role=TenantUserRole.MEMBER
            #     ), tenant_id=str(invitation.tenant))  # davetiyeden gelen tenant bilgisi olarak değiştirilmiştir.

        else:
            user_tenants = await self._messenger.find_by_user_id(user["id"])
            if not user_tenants:
                raise ValueError("Tenant not found for user")
                # raise ValueError(f"Tenant not found for user {user["id"]}")
            tenant_user_list = [tenant_user for tenant_user in user_tenants if tenant_user["role"] == TenantUserRole.OWNER]
            tenant_user = tenant_user_list[0]
            tenant_id = tenant_user["tenant_id"]

        # UserSessionClient oluşturulur. Bu durumda AthorizationCode oluşturulurken bu tenant kullanılacak
        user_session_client = await self._user_session_client_service.create(
            CreateUserSessionClient(
                user_session_id=user_session.id,
                client_id=auth_request.client.id,
                tenant=tenant_id,
                created_at=datetime.now(),
            )
        )

        auth_request.user_session = user_session
        return (tenant_id, user_session, auth_request)

    async def register(
        self, session_id: UUID, register_endpoint: RegisterEndpoint
    ) -> Tuple[UUID, UserSession, AuthorizeRequest]:
        """Sisteme yeni bir kullanıcı ekler"""
        try:
            # Gelen istek kontrol edilir
            val_result = await self._authorize_validator.validate(
                register_endpoint, session_id
            )
            if val_result.error:
                raise ValueError(val_result.error)
            auth_request: AuthorizeRequest = val_result.result

            # Kullanıcının var olup olmadığı kontrol edilir.
            user = await self._messenger.user_get_by_email(register_endpoint.email)
            if user:
                email = user["email"]
                raise NameError(f"{email} already exists")

            # Davet varsa kontrol edilir.
            invitation_id = auth_request.invitation
            invitation = (
                await self._get_invitation(invitation_id) if invitation_id else None
            )

            # Kullanıcı kaydedilir
            created_user = CreateUser(
                name=register_endpoint.name,
                surname=register_endpoint.surname,
                email=register_endpoint.email,
                password=register_endpoint.password,
                phone=register_endpoint.phone,
                email_verified=False,
            )
            if invitation_id:
                created_user.email_verified = True
            user = await self._messenger.create_user(created_user.model_dump(exclude_none=True))

            # client first_party ise yeni bir tenant oluşturulur
            tenant_name = user["email"].split("@")[0]
            queryArgs = QueryArgs(
                where=[
                    Filter(field="name", op=FilterOp.EQUAL, value=tenant_name),
                ]
            )
            some_tenant_count = await self._messenger.tenant_count(queryArgs.to_serialize())
            if some_tenant_count != 0:
                tenant_name += "-" + generate(
                    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", size=6
                )
            tenant_title = " ".join([user["name"], user["surname"]])
            tenant = await self._messenger.tenant_create(
                CreateTenant(name=tenant_name, user_id=user["id"], title=tenant_title).model_dump(exclude_none=True)
            )

            # Tenant kullanıcı oluşturulur.
            tenant_user = await self._messenger.tenant_user_create(
                CreateTenantUser(
                    user_id=user["id"], tenant_id=tenant["id"], role=TenantUserRole.OWNER
                ).model_dump(exclude_none=True),
                tenant_id=str(tenant["id"]),
            )

            # Eğer varolan bir session varsa kapatılır.
            user_session = auth_request.user_session
            if user_session:
                await self._user_session_service.update(
                    user_session.id, UpdateUserSession(authenticated=False)
                )

            authenticated_at = datetime.now()
            expired_at = authenticated_at + timedelta(minutes=self._session_timeout)
            user_session = await self._user_session_service.create(
                CreateUserSession(
                    id=uuid4(),
                    user_id=user["id"],
                    authenticated_at=authenticated_at,
                    expired_at=expired_at,
                    authenticated=True,
                )
            )
            auth_request.user_session = user_session

            # Kullanıcının default organization_type - organization ve organization_user bilgileri eklenir. (04.03.2023)
            organization_type = await self._messenger.organization_type_create(
                CreateOrganizationType(
                    name=tenant_name,
                    description=tenant_name,
                    is_root=True,
                ).model_dump(exclude_none=True),
                tenant_id=str(tenant["id"]),
            )

            organization = await self._messenger.organization_create(
                CreateOrganization(
                    name=tenant_name,
                    description=tenant_name,
                    is_root=True,
                    organization_type_id=organization_type["id"],
                    is_hierarchical=True,
                ).model_dump(exclude_none=True),
                tenant_id=str(tenant["id"]),
            )

            organization_user = await self._messenger.organization_user_create(
                CreateOrganizationUser(user_id=user["id"], organization_id=organization["id"]).model_dump(exclude_none=True),
                tenant_id=str(tenant["id"]),
            )

            # Davet varsa ilgili Tenant için TenantUser oluşturulur
            if invitation:
                guest_user = await self._messenger.tenant_user_create(
                    CreateTenantUser(
                        user_id=user["id"],
                        tenant_id=invitation["tenant"],
                        role=TenantUserRole.MEMBER,
                    ).model_dump(exclude_none=True),
                    tenant_id=str(invitation["tenant"]),
                )  # NOT : Davetiyeden gelen tenant bilgisi olarak değiştirilmiştir. (19.07.2023)
                tenant_user = guest_user

                # Eğer kullanıcı davet usulü ile geldiyse ekstra olarak davet sırasında seçilen organization'a user olarak eklenir. (04.03.2023)
                if invitation["organization_id"]:
                    organization_user_member = await self._messenger.organization_user_create(
                        CreateOrganizationUser(
                            user_id=user["id"], organization_id=invitation["organization_id"]
                        ).model_dump(exclude_none=True),
                        tenant_id=str(invitation["tenant"]),
                    )
                    invitation = await self._messenger.invitation_update(
                        str(invitation["id"]),
                        UpdateInvitation(used=True, organization_id=organization["id"]).model_dump(exclude_none=True),
                        tenant_id=str(invitation["tenant"]),
                    )

            # İstekte belirtilen client için user_session_client oluşturulur. Hangi tenant için
            # session olşturulacağı davetiye durumunda davet edilen tenant da session açılır. Davetiye yoksa
            # Yeni oluşturulan tenant da usersessionclient oluşturulur.
            user_session_client = await self._user_session_client_service.create(
                CreateUserSessionClient(
                    user_session_id=user_session.id,
                    client_id=auth_request.client.id,
                    tenant=tenant["id"],
                    created_at=datetime.now(),
                )
            )

            return tenant_user["tenant_id"], user_session, auth_request
        except ValueError:
            raise
        except NameError:
            raise
        except Exception as ex: 
            errors = []
            if "organization_user" in locals():
                if organization_user and organization_user.get("error") is None and organization_user.get("id"):
                    await self._messenger.delete_organization_user(organization_user["id"])
                elif organization_user and organization_user.get("error") is not None:   
                   errors.append(organization_user.get("error"))
            if "organization_type" in locals():
                if organization_type and organization_type.get("error") is None and organization_type.get("id"):
                    await self._messenger.delete_organization_type(organization_type["id"])
                elif organization_type and organization_type.get("error") is not None:
                   errors.append(organization_type.get("error"))
            if "organization" in locals():
                if organization and organization.get("error") is None and organization.get("id"):
                    await self._messenger.delete_organization(organization["id"])
                elif organization and organization.get("error") is not None:
                   errors.append(organization.get("error"))
            if "tenant_user" in locals():
                if tenant_user and tenant_user.get("error") is None and tenant_user.get("id"):
                    await self._messenger.delete_tenant_user(tenant_user["id"])
                elif tenant_user and tenant_user.get("error") is not None:
                   errors.append(tenant_user.get("error"))
            if "tenant" in locals():
                if tenant and tenant.get("error") is None and tenant.get("id"):
                    await self._messenger.delete_tenant(tenant["id"])
                elif tenant and tenant.get("error") is not None:
                   errors.append(tenant.get("error"))
            if "user" in locals():
                if user and user.get("error") is None and user.get("id"):
                    await self._messenger.delete_user(user["id"])
                elif user and user.get("error") is not None:
                   errors.append(user.get("error"))
                   
            if errors:
                raise Exception(" | ".join(errors))
            else: 
                raise ex


    async def consent(
        self, session_id: UUID, consent_endpoint: ConsentEndpoint
    ) -> Tuple[Consent, AuthorizeRequest]:
        """Onay işlemi"""

        # Gelen istek kontrol edilir
        val_result = await self._authorize_validator.validate(
            consent_endpoint, session_id
        )
        if val_result.error:
            raise ValueError(val_result.error)
        auth_request: AuthorizeRequest = val_result.result

        if not auth_request.user_session:
            raise ValueError(f"User session not found: {str(session_id)}")

        consent = await self._consent_service.find_by_keys(
            auth_request.client.id, auth_request.user_session.user_id
        )
        if not consent:
            consent = await self._consent_service.create(
                CreateConsent(
                    user_id=auth_request.user_session.user_id,
                    client_id=auth_request.client.id,
                    accepted=consent_endpoint.accepted,
                    scopes=auth_request.scopes,
                )
            )
        else:
            consent = await self._consent_service.update(
                consent.id,
                UpdateConsent(
                    scopes=auth_request.scopes, accepted=consent_endpoint.accepted
                ),
            )
        return (consent, auth_request)

    async def new_password(self, new_password_endpoint: NewPasswordEndpoint) -> User:
        """Token ile gelen email deki kişinin şifresini günceller"""

        token = jwt.decode(new_password_endpoint.token, self._jwt_secret, ["HS256"])
        expired_at = datetime.fromtimestamp(token["expired_at"])

        if expired_at < datetime.now():
            raise ValueError(f"token expired")

        user = await self._messenger.user_get_by_email(token["email"])

        if not user:
            raise ValueError(token["email"])

        return await self._messenger.update_password(
            user["id"], new_password_endpoint.password
        )

    async def _get_invitation(self, invitation_id: str) -> Any | None:
        invitation = await self._messenger.invitation_get(invitation_id)
        if not invitation:
            raise ValueError(f"{invitation_id} invitation not found")
        return invitation
