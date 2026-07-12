import sys
import os

sys.path.append(r"D:\Projeler\KABART\10_MAPA\mappa-enterprise-server\apps\manage")
try:
    from manage.config.app_container import AppContainer
    from manage.check_redirect_uris import check_redirect_uris

    container = AppContainer()
    alembic_url = container.config.alembic()["url"]

    name_list = ["manage", "workspace", "application"]
    domain = container.config.domain()
    check_redirect_uris(alembic_url, name_list, domain)
    print("Successfully ran check_redirect_uris")
except Exception as e:
    print(f"Error: {e}")
