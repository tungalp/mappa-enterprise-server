# Python Application oluşturulması \apps dizini içerisinde aşağıdaki komut çalıştırılır
poetry new [app_name]

# Python Application ayarlarının yapılması
yeni oluşan application dizini aşağıdaki gibi olmalıdır.
    apps\
        [app_name]\
                    [app_name]\
        test\
        pyproject.toml
        .
        .

# Python Application router ayarının yapılması
 libs\[app_name]\[app_name]\ klasörü içindeki dosyalar aşağıdaki gibi olmalıdır.
# __init__.py
    __version__ = '0.1.0'

# main.py
from [app_name].app import create_application

app = create_application()

@app.get("/")
async def root():
    """Root function

    Returns:
        Object: Dönüş mesajı
    """
    return {
        "msg": "Hello from [app_name]"
    }

# app.py
import [app_name]
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from [app_name].config.app_container import ApplicationContainer

app_props = {
    "title": "Mapa [app_name]",
    "description": "Mapa [app_name]",
    "version": "0.0.1",
    "terms_of_service": "http://mapa.com.tr/terms/",
    "contact": {
        "name": "Admin",
        "url": "http://mapa.com.tr/contact/",
        "email": "admin@mapa.com.tr",
    },
    "license_info": {
        "name": "Mapa Commercial Licenze",
        "url": "https://mapa.com.tr/licenses/mapa.html"
    },
    "root_path": ""
}

backend = OAuth2IdTokenBackend(
    jwks_uri="AUTH0 url"
)

def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = ApplicationContainer()
    container.wire(packages=[[app_name]])

    middleware = [
        Middleware(AuthenticationMiddleware, backend=backend),
    ]
    # Ana uygulama nesnesi
    application = FastAPI(**app_props, middleware=middleware)
    application.container = container  # type: ignore

    # Routes
   

    return application



# pyproject.toml dosyası ayarlanması
dosya içeriği aşağıdaki şekilde düzenlenir, varsa ek depend modül eklenir

[tool.poetry]
name = "app-[app_name]"
version = "0.1.3"
description = ""
authors = ["AUTHORS"]
packages = [
    { include = "[app_name]" },
]

[tool.poetry.dependencies]
python = "^3.10"
lib-app = {path = "../../libs/app", develop = true}
lib-core = {path = "../../libs/core", develop = true}
bcrypt = "^3.2.0"
PyJWT = "^2.4.0"

[tool.poetry.dev-dependencies]
pytest = "^6.2.5"
pytest-asyncio = "^0.18.1"
lib-test = {path = "../test"}

[tool.pytest.ini_options]
asyncio_mode = "auto"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

