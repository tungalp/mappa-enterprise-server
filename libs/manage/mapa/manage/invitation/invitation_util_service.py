from typing import Dict
import jwt
from datetime import datetime, timedelta
from mapa.core.data.base_service import BaseService
from mapa.core.data.query_args import QueryArgs, Filter, FilterOp
from mapa.manage.invitation.invitation_model import Invitation
from mapa.manage.organization.organization_model import Organization
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser
from mapa.manage.organization_user.organization_user_service import OrganizationUserService
from mapa.manage.tenant_user.tenant_user_model import CreateTenantUser, TenantUserRole
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.manage.user.user_model import UpdateUser
from mapa.manage.user.user_service import UserService
from mapa.manage.constants import PromptModes
from urllib import parse


class InvitationUtilService(BaseService):

    def __init__(self,
                 jwt_secret: str,
                 user_service: UserService,
                 tenant_user_service: TenantUserService,
                 organization_service: OrganizationService,
                 organization_user_service: OrganizationUserService) -> None:
        self._jwt_secret = jwt_secret
        self._user_service = user_service
        self._tenant_user_service = tenant_user_service
        self._organization_service = organization_service
        self._organization_user_service = organization_user_service
        super().__init__()

    async def create_invitation_link(self, app_host: str, invitation: Invitation) -> Dict[str, str]:

        data = {
            "email": invitation.email,
            "tenant_id": str(invitation.tenant),
            "expired_at": (invitation.expired_at).timestamp(),
            "invitation_id": str(invitation.id),
            "user_id": str(invitation.user_id),
        }

        token = jwt.encode(data, self._jwt_secret, "HS256")

        url = f"{app_host}/api/manage/user/invitation-redirect/?token={token}"
        return {
            "type": "redirect",
            "url": url
        }

    def create_invitation_link_redirect(self, app_host: str, screen_hint: str, invitation_id: str, email: str) -> Dict[str, str]:

        req = {
            "screen_hint": screen_hint,
            "invitation_id": invitation_id,
            "email": email
        }

        url = f"{app_host}/manage/invitation?{parse.urlencode(req)}"
        return {
            "type": "redirect",
            "url": url
        }

    async def check_invitation(self, token: str) -> Dict:
        """Token ile gelen davetiye bilgileri kontrol edilir"""
        screen_hint = f"{PromptModes.REGISTER}"

        token_decoded = jwt.decode(token, self._jwt_secret, ["HS256"])

        expired_at = datetime.fromtimestamp(token_decoded["expired_at"])
        tenant_id = token_decoded["tenant_id"]
        email = token_decoded["email"]
        user_id = token_decoded["user_id"]
        invitation_id = token_decoded["invitation_id"]

        if expired_at < datetime.now():
            raise ValueError(f"token expired")

        user = await self._user_service.get_by_email(email)
     
        # User bilgisi varsa Login'e yönlendirilmelidir.
        if user:
            user_id = user.id
            screen_hint = f"{PromptModes.LOGIN}"

            queryArgs = QueryArgs(
                where=[
                    Filter(field="tenant_id",
                           op=FilterOp.EQUAL, value=tenant_id),
                    Filter(field="user_id",
                           op=FilterOp.EQUAL, value=user.id)
                ]
            )

            # NOT : Aynı user 2. kez farklı bir tenant'a davet edildiği zaman ilgili TenantUser bilgisi varmı yokmu kontrol edilir. (19.07.2023)
            tenant_user_kontrol = await self._tenant_user_service.find(queryArgs, tenant_id=str(tenant_id))

            # NOT : Davet edilen kullanıcı sisteme davetiyeden önce giriş yapmış bir durumda ise login işlemine yönlendirilmeden önce davet edilen tenant'a member olarak eklenir. (02.08.2023)
            # NOT : Eğer aynı user 2. kez farklı bir tenant'a devet edilmiş olup ilgili TenantUser bilgisi yoksa TenantUser bilgisi oluşturulur. (19.07.2023)
            if not tenant_user_kontrol:
                guest_user = await self._tenant_user_service.create(CreateTenantUser(
                    user_id=user.id,
                    tenant_id=tenant_id,
                    role=TenantUserRole.MEMBER
                ), tenant_id=str(tenant_id))  # davetiyeden gelen tenant bilgisi olarak değiştirilmiştir.

            # NOT : Ilgili user'a bir davet geldiyse email_verified alanı true olarak güncellenir. (19.07.2023)
            if  user.email_verified == False:
                update_user = UpdateUser(email_verified=True)
                updated_user = await self._user_service.update(user.id, update_user)
                
        return {
            "screen_hint": screen_hint,
            "invitation_id": invitation_id,
            "email": email,
            "user_id": user_id,
            "tenant_id": str(tenant_id)
        }
