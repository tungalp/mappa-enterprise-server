import random
from typing import Any, List
from nanoid import generate
from uuid import UUID, uuid4
from mapa.manage.organization_client.organization_client_model import CreateOrganizationClient
from mapa.manage.organization_role.organization_role_model import CreateOrganizationRole
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.user_variable_type.user_variable_type_model import CreateUserVariableType



def generate_organization_type() -> CreateOrganizationType:
    return CreateOrganizationType(
        name="organization_type_test_app"+generate(size=4),
        description="Test"+generate(size=4),
        is_root=False) 

def generate_organization(organization_type_id: UUID = uuid4()) -> CreateOrganization:
    return CreateOrganization(
        name="organiza_test_app"+generate(size=4),
        description="Test"+generate(size=4),
        is_root=False,
        organization_type_id=organization_type_id) 

def generate_organization_user(user_id: UUID = uuid4(),organization_id: UUID = uuid4()) -> CreateOrganizationUser:
    return CreateOrganizationUser(
        organization_id=organization_id,
        user_id=user_id)
    
def generate_organization_role(role_id: UUID = uuid4(),organization_id: UUID = uuid4()) -> CreateOrganizationRole:
    return CreateOrganizationRole(
        organization_id=organization_id,
        role_id=role_id)
    
        
def generate_organization_client(client_id: UUID = uuid4(),organization_id: UUID = uuid4()) -> CreateOrganizationClient:
    return CreateOrganizationClient(
        organization_id=organization_id,
        client_id=str(client_id))
    
        
def generate_user_variable_type(name:str, description:str ) -> CreateUserVariableType:
    return CreateUserVariableType(
        name=name,
        description=description)
    

api_scopes = ["query:api", "edit:api", "query:api_scope", "edit:api_scope", "query:client", "edit:client", "query:client_api", "edit:client_api", "query:client_api_scope", "edit:client_api_scope", "query:invitation", "edit:invitation", "query:profile_adaptor", "edit:profile_adaptor", "query:role", "edit:role", "query:role_api_scope", "edit:role_api_scope", "query:role_user", "edit:role_user", "query:user", "edit:user", "query:application", "edit:application", "query:content_page", "edit:content_page", "query:content_page_template", "edit:content_page_template", "query:connection_info", "edit:connection_info", "query:context_var", "edit:context_var",
              "query:gateway_api", "edit:gateway_api", "query:integration", "edit:integration", "query:parameter_mapping", "edit:parameter_mapping", "query:route", "edit:route", "query:base_layer", "edit:base_layer", "query:bookmark", "edit:bookmark", "query:connection", "edit:connection", "query:definition", "edit:definition", "query:hook", "edit:hook", "query:layer", "edit:layer", "query:layer_definition", "edit:layer_definition", "query:layer_hook", "edit:layer_hook", "query:map", "edit:map", "query:map_base_layer", "edit:map_base_layer", "query:map_layer", "edit:map_layer", "query:namespace", "edit:namespace", "query:reference", "edit:reference",
              "query:organization","edit:organization","query:organization_user","edit:organization_user","query:organization_type","edit:organization_type","query:organization_role","edit:organization_role","query:organization_client","edit:organization_client","query:user_variable_type","edit:user_variable_type"]


instances = []
