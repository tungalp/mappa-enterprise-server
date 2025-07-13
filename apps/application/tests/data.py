from mapa.application.app.app_model import CreateApp
from mapa.application.constants import ContentPageType
from mapa.application.content_page.content_page_model import CreateContentPage
from nanoid import generate
from uuid import UUID, uuid4

from mapa.application.content_page_template.content_page_template_model import CreateContentPageTemplate

tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"
instances = []


def generate_content_page(app_id: UUID) -> CreateContentPage:
    return CreateContentPage(
        name="app_test_"+generate(size=4),
        title="Koydes App",
        description="test",
        app_id=app_id,
        scope="page:read",
        designer_schema=get_designer_schema(),
        path="",
        query="",
        type=ContentPageType.PAGE
    )

def generate_content_page_template() -> CreateContentPageTemplate:
    return CreateContentPageTemplate(
        name="app_test_"+generate(size=4),
        title="Koydes App",
        description="test",
        designer_schema=get_designer_schema(),
        type=ContentPageType.PAGE
    )


def generate_app() -> CreateApp:
    return CreateApp(
        name="app_test_"+generate(size=4),
        code="app_test_"+generate(size=4),
        title="Koydes App",
        description="test",
        identifier="http://baseurl"+generate(size=4),
        menu=get_menu_data(),
        logout_uri="http://test",
        return_uri="http://return",
        logo="https://www.mapa.com.tr/application/views/islemgis/layouts/images/logo-colored.png",
        translation={},
        ordr=1)  # type: ignore


def get_menu_data():
    return {
        "name": "Koydes Root",
        "description": "Root",
        "title": "koydes",
        "key": "koydes",
        "children": [
            {
                "name": "Koydes Tanımlar",
                "description": "Tanımlar",
                "title": "Tanımlar",
                "key": "koydestanimlar",
                "children": [
                    {
                        "name": "Koydes Tanımlar Tip",
                        "description": "Tanımlar Tip",
                        "title": "Tipler",
                        "key": "koydestanimlartip"
                    }
                ]
            }
        ]
    }, {
        "name": "Koydes Harita",
        "description": "Harita",
        "title": "koydesharita",
        "key": "koydesharita",
        "children": [
            {
                "name": "Koydes Envanter Harita",
                "description": "Envanter Harita",
                "title": "koydesenvanterharita",
                "key": "koydesenvanterharita",
                "children": [
                    {
                        "name": "Koydes Proje Harita",
                        "description": "Proje Harita",
                        "title": "koydesprojeharita",
                        "key": "koydesprojeharita"
                    },
                ]
            },
        ]
    }


def get_designer_schema():
    return {
        "data": {
            "fields": {"type": "object", "properties": {"adi": {"type": "string", "title": "Adı", "x-decorator": "FormItem", "x-component": "Input", "x-validator": [], "x-component-props": {}, "x-decorator-props": {}, "name": "adi", "description": "", "enum": [], "required": True, "x-designable-id": "mdazxyh5mx4", "x-index": 0}, "soyadi": {"type": "string", "title": "Soyadı", "x-decorator": "FormItem", "x-component": "Input", "x-validator": [], "x-component-props": {}, "x-decorator-props": {}, "name": "soyadi", "required": True, "x-designable-id": "170euocmt17", "x-index": 1}, "aciklama": {"type": "string", "title": "Açıklama", "x-decorator": "FormItem", "x-component": "Input.TextArea", "x-validator": [], "x-component-props": {}, "x-decorator-props": {}, "name": "aciklama", "x-designable-id": "5w3ycgyxp3n", "x-index": 2}}, "x-designable-id": "igfv88s6har"},
            "form": {"labelCol": 6, "wrapperCol": 12},
            "html": None}
    }

api_scopes = ["query:api", "edit:api", "query:api_scope", "edit:api_scope", "query:client", "edit:client", "query:client_api", "edit:client_api", "query:client_api_scope", "edit:client_api_scope", "query:invitation", "edit:invitation", "query:profile_adaptor", "edit:profile_adaptor", "query:role", "edit:role", "query:role_api_scope", "edit:role_api_scope", "query:role_user", "edit:role_user", "query:user", "edit:user", "query:application", "edit:application", "query:content_page", "edit:content_page", "query:content_page_template", "edit:content_page_template", "query:connection_info", "edit:connection_info", "query:context_var", "edit:context_var",
              "query:gateway_api", "edit:gateway_api", "query:integration", "edit:integration", "query:parameter_mapping", "edit:parameter_mapping", "query:route", "edit:route", "query:base_layer", "edit:base_layer", "query:bookmark", "edit:bookmark", "query:connection", "edit:connection", "query:definition", "edit:definition", "query:hook", "edit:hook", "query:layer", "edit:layer", "query:layer_definition", "edit:layer_definition", "query:layer_hook", "edit:layer_hook", "query:map", "edit:map", "query:map_base_layer", "edit:map_base_layer", "query:map_layer", "edit:map_layer", "query:namespace", "edit:namespace", "query:reference", "edit:reference"]

