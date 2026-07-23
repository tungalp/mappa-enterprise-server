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

    # In production (MAPA_ENV=PRODUCTION), do NOT add -dev.mapaenterprise.com URIs
    # to the SSO whitelist — they are a security risk in a live environment.
    is_production = os.environ.get("MAPA_ENV", "").upper() == "PRODUCTION"
    include_dev_uris = not is_production

    check_redirect_uris(alembic_url, name_list, domain, include_dev_uris=include_dev_uris)
    env_label = "PRODUCTION" if is_production else "DEVELOPMENT"
    print(f"Successfully ran check_redirect_uris [{env_label}] (include_dev_uris={include_dev_uris})")
except Exception as e:
    print(f"Error: {e}")

