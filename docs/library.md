# Python Library oluşturulması \libs dizini içerisinde aşağıdaki komut çalıştırılır
poetry new [app_name]

# Python Library ayarlarının yapılması
yeni oluşan library dizini aşağıdaki yapıya taşınır. libs\mapa dizini oluşturulur. libs\[app_name]\ klasörü, libs\mapa\[app_name] altına taşınır
    libs\
        mapa\
            [app_name]
        test\
        pyproject.toml
        .
        .

# pyproject.toml dosyası ayarlanması
dosya içeriği aşağıdaki şekilde düzenlenir, varsa ek depend modül eklenir

[tool.poetry]
name = "lib-[app_name]"
version = "0.1.3"
description = ""
authors = ["AUTHORS"]
packages = [
    { include = "mapa" },
]

[tool.poetry.dependencies]
python = "^3.10"
lib-core = {path = "../core"}
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

