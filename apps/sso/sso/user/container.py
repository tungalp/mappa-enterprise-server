from dependency_injector import containers
from dependency_injector import providers

class UserContainer(containers.DeclarativeContainer):
    """Kullanıcı paketinin bağımlılık konteyneri

    """
    messenger = providers.Dependency()
