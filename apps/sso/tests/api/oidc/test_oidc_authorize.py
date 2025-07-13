from uuid import uuid4
import pytest
from mapa.sso.constants import AuthorizeErrors, PromptModes, ResponseModes
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from mapa.sso.oidc.oidc_service import OidcService
from mapa.sso.oidc.response_handling.authorize_response import AuthorizeResponse
from mapa.sso.oidc.response_handling.interaction_response import InteractionResponse
from mapa.sso.oidc.results.authorize_result import AuthorizeResult
from .oidc import create_service
from ..conftest import SsoFixture


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

@pytest.mark.asyncio
async def test_authorize_code_login(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint = fixture.create_authorize_endpoint()
    session_id = None
    response, error_response = await service.authorize(authorize_endpoint, session_id)
   
    assert response is not None
    assert isinstance(response, InteractionResponse)
    assert error_response is None
    
    # Autorization Result
    auth_result = AuthorizeResult("http://sso.test.com")
    response_dict = auth_result.execute(authorize_endpoint, response)
    
    assert response_dict["type"] == "redirect"
    assert response_dict["url"] is not None
    assert "login" in response_dict["url"]    

@pytest.mark.asyncio
async def test_authorize_code_flow_query(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint = fixture.create_authorize_endpoint()
    authorize_endpoint.response_mode = ResponseModes.QUERY
    session_id = fixture.session_id
    response, error_response = await service.authorize(authorize_endpoint, session_id)
   
    assert response is not None
    assert isinstance(response, AuthorizeResponse)
    assert error_response is None
    
    # Autorization Result
    auth_result = AuthorizeResult("http://sso.test.com/")
    response_dict = auth_result.execute(authorize_endpoint, response)
    
    assert response_dict["type"] == "redirect"
    assert response_dict["url"] is not None
    assert "code=" in response_dict["url"]
    
    
@pytest.mark.asyncio
async def test_authorize_code_flow_fragment(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint = fixture.create_authorize_endpoint()
    authorize_endpoint.response_mode = ResponseModes.FRAGMENT
    session_id = fixture.session_id
    response, error_response = await service.authorize(authorize_endpoint, session_id)
   
    assert response is not None
    assert isinstance(response, AuthorizeResponse)
    assert error_response is None
    
    # Autorization Result
    auth_result = AuthorizeResult("http://sso.test.com/")
    response_dict = auth_result.execute(authorize_endpoint, response)
    
    assert response_dict["type"] == "redirect"
    assert response_dict["url"] is not None
    assert "code=" in response_dict["url"]
    assert "#" in response_dict["url"]
    
@pytest.mark.asyncio
async def test_authorize_code_web_message(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint = fixture.create_authorize_endpoint()
    authorize_endpoint.response_mode = "web_message"
    session_id = fixture.session_id
    response, error_response = await service.authorize(authorize_endpoint, session_id)
   
    assert response is not None
    assert isinstance(response, AuthorizeResponse)
    assert error_response is None

    # Autorization Result
    auth_result = AuthorizeResult("http://sso.test.com/")
    response_dict = auth_result.execute(authorize_endpoint, response)
    
    assert response_dict["type"] == "html"
    assert response_dict["content"] is not None

        
@pytest.mark.asyncio
async def test_authorize_error(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint = fixture.create_authorize_endpoint()
    authorize_endpoint.client_id = "test_client_id"
    session_id = uuid4()
    response, error_response = await service.authorize(authorize_endpoint, session_id)
    
    assert response is None
    assert error_response is not None
    
@pytest.mark.asyncio
async def test_authorize_prompt_none(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint: AuthorizeEndpoint = fixture.create_authorize_endpoint()
    authorize_endpoint.prompt = PromptModes.NONE
    session_id = uuid4()
    response, error_response = await service.authorize(authorize_endpoint, session_id)

    assert error_response is not None
    assert response is None    

@pytest.mark.asyncio
async def test_authorize_prompt_none_login(fixture: SsoFixture):
    """Service"""
    
    service: OidcService = await create_service(fixture)
    assert service is not None

    authorize_endpoint: AuthorizeEndpoint = fixture.create_authorize_endpoint()
    authorize_endpoint.prompt = f"{PromptModes.LOGIN} {PromptModes.NONE}"
    session_id = uuid4()
    esponse, error_response = await service.authorize(authorize_endpoint, session_id)
    
    assert error_response is not None
    assert AuthorizeErrors.INTERACTION_REQUIRED in error_response.error
    
    """
1- https://kgulenc.auth0.com/authorize   302
/login?state=hKFo2SBaV2NoblU2RXFGOHJ1c1Nqb0htUkVjdmc5OWZYN3hFQqFupWxvZ2luo3RpZNkgY3o5ZnB3TkI4eXRFOEoxeEJ3VkhNUE01VWx0TGh5aEGjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ&client=hHH247IlLbsiP6HeUzMLr7kbN2j668JI&protocol=oauth2&audience=https%3A%2F%2Ftest-server-2%2Fapi%2Fv1&redirect_uri=http%3A%2F%2Flocalhost%3A3000&scope=openid%20profile%20email&response_type=code&response_mode=query&nonce=UzNRYTdneS1UbmNlczJZTVZtd0N1M2hMamMtZUhLdzhGSktuMWZpaUxORA%3D%3D&code_challenge=N0zbpqHEWOKbncNegvcLO6ghlIKVz2Goo-85R1dy5qQ&code_challenge_method=S256&auth0Client=eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ%3D%3D    

audience: https://test-server-2/api/v1
client_id: hHH247IlLbsiP6HeUzMLr7kbN2j668JI
redirect_uri: http://localhost:3000
scope: openid profile email
response_type: code
response_mode: query
state: OFZydXMxSXJVbUUzYzlldm9yVFZ4ZzR5ZV9jRlM0ZlF0ZUhGaW10RmNfWg==
nonce: SXFWdXJzOXpJMDhrRVAtR2xYRjdnVXFZTVI1aE9pNVVxeG1ndjhmMTRkeQ==
code_challenge: xp2srd7EdBqz9yWEAgS0o_9yab2K1xudkKHYLHJAXtA
code_challenge_method: S256
auth0Client: eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ==
    """
    
    """
    
2- https://kgulenc.auth0.com/login (GET) 200 (Login UI)

state: hKFo2SBONWlIdGpuYUloakhkeFQ2b2wtVXJVaktHT2FOWERfaaFupWxvZ2luo3RpZNkgczNLMUZLZUdCZnNOalB6cTFGd0Fuc1pPUm9XbFNNbkmjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ
client: hHH247IlLbsiP6HeUzMLr7kbN2j668JI
protocol: oauth2
audience: https://test-server-2/api/v1
redirect_uri: http://localhost:3000
scope: openid profile email
response_type: code
response_mode: query
nonce: b3cuUGZmcjAydE5uajYyVmVvbk5xSzhmLUdXblYzYjVuSnFMSFFDbDhnbQ==
code_challenge: M3f8_HRheur3eavo9tXolu6oc98swh1bIUpGHl4_ctQ
code_challenge_method: S256
auth0Client: eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ==
    """
    
    """
    3- https://kgulenc.auth0.com/usernamepassword/login (POST) 200
    
<form method="post" name="hiddenform" action="https://kgulenc.auth0.com/login/callback">
    <input type="hidden" name="wa" value="wsignin1.0">
    <input type="hidden" 
           name="wresult" 
           value="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiNWJjYjliYjk0YzI1NzY1ZThkYzc1ZTAzIiwiZW1haWwiOiJrdW50YXlndWxlbmNAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImxhc3RfcGFzc3dvcmRfcmVzZXQiOiIyMDIyLTAzLTE2VDA4OjAwOjE3LjY4MloiLCJzaWQiOiJ0RXZoUzBNSFZFWm1DRjI2SjVXNFJUVTNHZ2dDc3NxMiIsImlhdCI6MTY1MDc4MzUyMywiZXhwIjoxNjUwNzgzNTgzLCJhdWQiOiJ1cm46YXV0aDA6a2d1bGVuYzpVc2VybmFtZS1QYXNzd29yZC1BdXRoZW50aWNhdGlvbiIsImlzcyI6InVybjphdXRoMCJ9.siyAsCZwLAlXKON9nWQNd2g1itMIxVpBlLzHcR4QAM49efAIBlCf-wdxHUq1K0el2EhEX4oudLbQuzCoYxYpfOhYcqUjD1taW_lngeJiYuoam0SVgFjyaxZOe49tG1AhI8kFrNAQPjn5g63aYQOgykmN4TJr4RH_vlCOVizWass">
    <input type="hidden" name="wctx" value="{&#34;strategy&#34;:&#34;auth0&#34;,&#34;auth0Client&#34;:&#34;eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAiLCJlbnYiOnsibG9jay5qcy11bHAiOiIxMS4zMC42IiwiYXV0aDAuanMtdWxwIjoiOS4xNi40In19&#34;,&#34;tenant&#34;:&#34;kgulenc&#34;,&#34;connection&#34;:&#34;Username-Password-Authentication&#34;,&#34;client_id&#34;:&#34;hHH247IlLbsiP6HeUzMLr7kbN2j668JI&#34;,&#34;response_type&#34;:&#34;code&#34;,&#34;response_mode&#34;:&#34;query&#34;,&#34;scope&#34;:&#34;openid profile email&#34;,&#34;protocol&#34;:&#34;oauth2&#34;,&#34;redirect_uri&#34;:&#34;http://localhost:3000&#34;,&#34;state&#34;:&#34;hKFo2SBaV2NoblU2RXFGOHJ1c1Nqb0htUkVjdmc5OWZYN3hFQqFupWxvZ2luo3RpZNkgY3o5ZnB3TkI4eXRFOEoxeEJ3VkhNUE01VWx0TGh5aEGjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ&#34;,&#34;nonce&#34;:&#34;UzNRYTdneS1UbmNlczJZTVZtd0N1M2hMamMtZUhLdzhGSktuMWZpaUxORA==&#34;,&#34;sid&#34;:&#34;tEvhS0MHVEZmCF26J5W4RTU3GggCssq2&#34;,&#34;audience&#34;:&#34;https://test-server-2/api/v1&#34;,&#34;realm&#34;:&#34;Username-Password-Authentication&#34;}">
    <noscript>
        <p>
            Script is disabled. Click Submit to continue.
        </p><input type="submit" value="Submit">
    </noscript>
</form>
    
audience: "https://test-server-2/api/v1"
auth0Client: "eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ=="
client_id: "hHH247IlLbsiP6HeUzMLr7kbN2j668JI"
code_challenge: "5HzDfUIN-jiZVilXamD9MmNecIo22piOICIcGEOKnyg"
code_challenge_method: "S256"
connection: "Username-Password-Authentication"
nonce: "dUZEOF9oeXlqemFrQzBiZFVLZ35+bTJUSVJ2bVR5fkJSTFhwTEE0MGl2Uw=="
password: "1.EceBade.1"
popup_options: {}
protocol: "oauth2"
redirect_uri: "http://localhost:3000"
response_mode: "query"
response_type: "code"
scope: "openid profile email"
sso: true
state: "hKFo2SBSMjhQbUFYOWlMQ0xRRUJIVHcyZ3RFUjhMTndJSldNcqFupWxvZ2luo3RpZNkgNVR0NHhRQUlSMWpRSURDN1VuU3A5aWRjd29OZlVWcDmjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ"
tenant: "kgulenc"
username: "kuntaygulenc@gmail.com"
_csrf: "FPjPO4XV-PHNve6fY4Y2r_9U684JXEZM98bg"
_intstate: "deprecated"
    """
    
    """
4- https://kgulenc.auth0.com/login/callback (POST) 302

    /authorize/resume?state=5Tt4xQAIR1jQIDC7UnSp9idcwoNfUVp9
    
wa: wsignin1.0
wresult: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiNWJjYjliYjk0YzI1NzY1ZThkYzc1ZTAzIiwiZW1haWwiOiJrdW50YXlndWxlbmNAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImxhc3RfcGFzc3dvcmRfcmVzZXQiOiIyMDIyLTAzLTE2VDA4OjAwOjE3LjY4MloiLCJzaWQiOiJsUjM5N1ZULXJIRU1DalJzaG1ObWhVc1NmemFwM0lRbiIsImlhdCI6MTY1MDc4MTgwNCwiZXhwIjoxNjUwNzgxODY0LCJhdWQiOiJ1cm46YXV0aDA6a2d1bGVuYzpVc2VybmFtZS1QYXNzd29yZC1BdXRoZW50aWNhdGlvbiIsImlzcyI6InVybjphdXRoMCJ9.B45kBvDZeP2HobWM1Rv-FF8rucFpeuFVzCmYtSMeP5E19Z42MFReUoRDeNq5Zo5wKIyLd6y7sdYTYqa3VRNaaUIR2kq9FdVljOP-asdEhs20vLsP8j75hrbxcY-RgGy2Ho5M-kzkpeqfDi0Op7DGR4JV6AEgjBc5_QdjGQR4s5U
wctx: {"strategy":"auth0","auth0Client":"eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAiLCJlbnYiOnsibG9jay5qcy11bHAiOiIxMS4zMC42IiwiYXV0aDAuanMtdWxwIjoiOS4xNi40In19","tenant":"kgulenc","connection":"Username-Password-Authentication","client_id":"hHH247IlLbsiP6HeUzMLr7kbN2j668JI","response_type":"code","response_mode":"query","scope":"openid profile email","protocol":"oauth2","redirect_uri":"http://localhost:3000","state":"hKFo2SBSMjhQbUFYOWlMQ0xRRUJIVHcyZ3RFUjhMTndJSldNcqFupWxvZ2luo3RpZNkgNVR0NHhRQUlSMWpRSURDN1VuU3A5aWRjd29OZlVWcDmjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ","nonce":"dUZEOF9oeXlqemFrQzBiZFVLZ35+bTJUSVJ2bVR5fkJSTFhwTEE0MGl2Uw==","sid":"lR397VT-rHEMCjRshmNmhUsSfzap3IQn","audience":"https://test-server-2/api/v1","realm":"Username-Password-Authentication"}    
    """
    
    """
5- https://kgulenc.auth0.com/authorize/resume?state=cz9fpwNB8ytE8J1xBwVHMPM5UltLhyhA  (GET) 302

    http://localhost:3000/?code=WsRG7ecnV5qfcghX&state=TzFuZ1JmUTRmSHF1ZFpwNlBuTWcyXzdZVmFGYWlVa2sxdmVhUW5yMVpyQg%3D%3D
    """
    
    """
6- http://localhost:3000/?code=WsRG7ecnV5qfcghX&state=TzFuZ1JmUTRmSHF1ZFpwNlBuTWcyXzdZVmFGYWlVa2sxdmVhUW5yMVpyQg%3D%3D    (GET) 300

    """
    
    
    
    
    """
    
    Login olduktan sonra tekrar uygulamaya girince
    https://kgulenc.auth0.com/authorize
    
audience: https://test-server-2/api/v1
client_id: hHH247IlLbsiP6HeUzMLr7kbN2j668JI
redirect_uri: http://localhost:3000
scope: openid profile email
response_type: code
response_mode: web_message
state: Y2JGOTFrbi0zT2Raa0x1T2lSUUttbWd5ZFcwUTU3YUdWa0lWZmlMN3l+WA==
nonce: N1hOVjk1RFkyXzZYbXRBSGdjWEg2YUI4ZC02ZS4xcnpNeTBLdnIuWTZxbg==
code_challenge: v5fWcvJfpewyiljSAYKkBiW8Ji5l00x9coHIcqVwprA
code_challenge_method: S256
prompt: none
auth0Client: eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ==
    
    """
    
    """
    Logout işlemi
1 -    https://kgulenc.auth0.com/v2/logout (GET) 302

http://localhost:3000


returnTo: http://localhost:3000
client_id: hHH247IlLbsiP6HeUzMLr7kbN2j668JI
auth0Client: eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ==

    """
    
    
    """
    Signup
    
1- https://kgulenc.auth0.com/dbconnections/signup POST 200

Response 

{"_id":"626548eaf1aa4f00696d578d","email_verified":false,"email":"kgulenc@fjsdfjslfjdkfjsd.com"}

{client_id: "hHH247IlLbsiP6HeUzMLr7kbN2j668JI",…}
client_id: "hHH247IlLbsiP6HeUzMLr7kbN2j668JI"
connection: "Username-Password-Authentication"
email: "kgulenc@fjsdfjslfjdkfjsd.com"
password: "1.Ecesdfsdfs"
state: "hKFo2SAwbmZ3Mk01M3lhTVhnb1NfaTdoc0pxc0t6NnlKcWdLU6FupWxvZ2luo3RpZNkgQXBkTUw5MmNlalZ0ejlibUpMWG5Tb29VbEZRbk90RXmjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ"    
    """
    
    """
2- https://kgulenc.auth0.com/usernamepassword/login (POST) 
    
audience: "https://test-server-2/api/v1"
auth0Client: "eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMS45LjAifQ=="
client_id: "hHH247IlLbsiP6HeUzMLr7kbN2j668JI"
code_challenge: "3DWvTQJ6xRPZ7TFFw93qur8QUm2UXdAkdb6ouiU8EC0"
code_challenge_method: "S256"
connection: "Username-Password-Authentication"
nonce: "MGt0ZVN1Ui41T2Z0ai03Q0Jpa0Y4OFo2bkdzYVNoTGNoY2N0Uzc2VkJkYg=="
password: "1.Ecesdfsdfs"
popup_options: {}
protocol: "oauth2"
redirect_uri: "http://localhost:3000"
response_mode: "query"
response_type: "code"
scope: "openid profile email"
sso: true
state: "hKFo2SAwbmZ3Mk01M3lhTVhnb1NfaTdoc0pxc0t6NnlKcWdLU6FupWxvZ2luo3RpZNkgQXBkTUw5MmNlalZ0ejlibUpMWG5Tb29VbEZRbk90RXmjY2lk2SBoSEgyNDdJbExic2lQNkhlVXpNTHI3a2JOMmo2NjhKSQ"
tenant: "kgulenc"
username: "kgulenc@fjsdfjslfjdkfjsd.com"
_csrf: "dK9eTp3D-XrwMCHYOfIoi70L9k9Qbloy64zo"
_intstate: "deprecated"    
    """