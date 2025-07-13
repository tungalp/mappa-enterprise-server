from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.invitation.invitation_service import InvitationService
from mapa.manage.invitation.mail_service import MailService

class InvitationContainer(containers.DeclarativeContainer):
    """Invitation paketinin bağımlılık konteyneri

    """
    
    config = providers.Configuration()
    
    database = providers.Dependency()
    invitation_util_service = providers.Dependency()
    
    invitation_service = providers.Factory(
        InvitationService,
        async_db=database
    )

    mail_service = providers.Factory(
        MailService,
        smtp = config.mail.smtp,
        port = config.mail.port,
        user_name = config.mail.user_name,
        password = config.mail.password,
        method = config.mail.method,
        subject = config.mail.subject,
        mail_header = config.mail.mail_header,
        mail_header_en = config.mail.mail_header_en,
        
    )