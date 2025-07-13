import json
from string import Template
from typing import Any, Dict, Union
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.constants import ResponseModes
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from urllib.parse import urlencode, urlparse
from mapa.sso.oidc.response_handling.authorize_error_response import AuthorizeErrorResponse
from mapa.sso.oidc.response_handling.authorize_response import AuthorizeResponse
from mapa.sso.oidc.response_handling.interaction_response import InteractionResponse


class AuthorizeResult:
    """Authorize metodunun dönüş nesnesi"""

    def __init__(self, app_host: str) -> None:
        self._app_host = app_host

    def  execute(
        self,
        endpoint: AuthorizeEndpoint,
        response: AuthorizeResponse | InteractionResponse) -> Any:
        """Response nesnesinden dönüş değeri oluşturur.
        Response_mode bilgisine göre redirect ya da html response oluşturulur."""

        response_dict = self.__to_dict(endpoint)
        if isinstance(response, AuthorizeResponse):
            return self._execute_authorize(endpoint, response)
        elif isinstance(response, InteractionResponse):
            return self._execute_interaction(response_dict, response)
        
    def execute_error(self, endpoint: Any, error: AuthorizeErrorResponse) -> Any:
        """Hata bilgisi url olarak oluşturulur."""
        endpoint_dict = self.__to_dict(endpoint)
        return self._build_error_response(endpoint_dict, error)
    
    def execute_login(self, endpoint: LoginEndpoint, response: InteractionResponse) -> Any:
        """Login"""
        endpoint_dict = self.__to_dict(endpoint)
        del endpoint_dict["email"]
        del endpoint_dict["password"]
        return self._execute_interaction(endpoint_dict, response)
    
    def execute_consent(self, endpoint: ConsentEndpoint, response: InteractionResponse) -> Any:
        """Login"""
        endpoint_dict = self.__to_dict(endpoint)
        del endpoint_dict["accepted"]
        return self._execute_interaction(endpoint_dict, response)    

    def _execute_authorize(self, endpoint: AuthorizeEndpoint, response: AuthorizeResponse) -> Dict[str, Any]:
        """Authorize dönüş değeri"""

        ret_val: Dict[str, Any]
        response_mode = endpoint.response_mode
        if (response_mode == ResponseModes.QUERY or response_mode == ResponseModes.FRAGMENT):
            ret_val = self._build_authorize_redirect_response(endpoint, response)
        else:
            ret_val = self._build_authorize_html_response(endpoint, response)
        return ret_val

    def _execute_interaction(self, endpoint: Dict[str, Any], response: InteractionResponse) -> Any:
        """Interaction için dönüş url bilgisi"""

        uri = f"{self._app_host}/{response.prompt}"

        if endpoint["response_mode"] == ResponseModes.QUERY:
            uri += ("?" + urlencode(endpoint))
        else:
            uri += ("#" + urlencode(endpoint))

        return {
            "type": "redirect",
            "url": uri
        }

    def _build_error_response(self, endpoint: Dict[str, Any], response: AuthorizeErrorResponse) -> Any:
        """Hata durumunda state bilgisi ile beraber hata redirect_uri adresine döndürülür"""
        uri = endpoint["redirect_uri"]
        response_dict = dict(response)
        response_dict["state"] = endpoint["state"]
        if endpoint["language"] is not None:
            response_dict["language"] = endpoint["language"]
        
        if endpoint["response_mode"] == ResponseModes.QUERY:
            uri += ("?" + urlencode(response_dict))
        else:
            uri += ("#" + urlencode(response_dict) + "#_=_")

        return {
            "type": "redirect",
            "url": uri
        }

    def _build_authorize_redirect_response(self, endpoint: AuthorizeEndpoint, response: AuthorizeResponse) -> Any:
        uri = endpoint.redirect_uri
        
        if endpoint.language is not None:
            response.language = endpoint.language
            
        response_dict = response.dict(exclude_none=True, exclude_unset=True)
        if endpoint.response_mode == ResponseModes.QUERY:
            uri += ("?" + urlencode(response_dict))
        else:
            uri += ("#" + urlencode(response_dict))

        return {
            "type": "redirect",
            "url": uri
        }

    def _build_authorize_html_response(self, endpoint: AuthorizeEndpoint, response: AuthorizeResponse) -> Any:
        content = Template("""
<html>
    <head>
    </head>
    <body>
        <script type="text/javascript">
            (function(window, document) {
              var targetOrigin = "$target_origin";
              var webMessageRequest = {};
              var authorizationResponse = {
                type: "authorization_response",
                response: $response
              };
              var mainWin = (window.opener) ? window.opener : window.parent;
              if (webMessageRequest["web_message_uri"] && webMessageRequest["web_message_target"]) {
                window.addEventListener("message", function(evt) {
                  if (evt.origin != targetOrigin)return;
                  switch (evt.data.type) {
                    case "relay_response":
                      var messageTargetWindow = evt.source.frames[webMessageRequest["web_message_target"]];
                      if (messageTargetWindow) {
                        messageTargetWindow.postMessage(authorizationResponse, webMessageRequest["web_message_uri"]);
                        window.close();
                      }
                    break;
                  }
                });
                mainWin.postMessage({
                  type: "relay_request"
                }, targetOrigin);
              } else {
                mainWin.postMessage(authorizationResponse, targetOrigin);
              }
            })(this, this.document);
        </script>
    </body>
</html>

            """)

        ret_val = content.substitute(
            target_origin=self.__extract_host(endpoint.redirect_uri),
            response=json.dumps(self.__to_dict(response)))

        return {
            "type": "html",
            "content": ret_val
        }

    def __to_dict(self, obj: Any) -> Dict[str, Any]:
        return dict(filter(lambda item: item[1] is not None, vars(obj).items()))
    
    def __extract_host(self, url: str) -> str:
        result = urlparse(url)
        # return f"{result.scheme}://{result.hostname}{'' if result.port in [80, 443] else ':' + str(result.port)}"
        return f"{result.scheme}://{result.hostname}:{result.port}"