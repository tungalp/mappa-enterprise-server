import sys
sys.path.insert(0, '/workspace/apps/sso')

from fastapi.testclient import TestClient
from sso.main import app

client = TestClient(app)

params = {
    "response_type": "code",
    "client_id": "client_id_qgis_plugin",
    "redirect_uri": "http://localhost:8787",
    "state": "-z6UTdDRIlP0e3N2Pl4n7Q",
    "nonce": "d7ft3se55w2_7dtXbq0q9w",
    "audience": "https://test-server/api/v1",
    "scope": "openid profile email offline_access",
    "response_mode": "query",
    "code_challenge_method": "S256",
    "code_challenge": "mI9EeUJ09JYO_GIK8RGgHQBIOmuqU8jm_6gPQx3Yuyo",
    "language": "tr"
}

print("1. Sending GET /api/sso/oidc/authorize...")
try:
    response = client.get("/api/sso/oidc/authorize", params=params, follow_redirects=False)
    print(f"GET Response Status: {response.status_code}")
    print(f"GET Response Headers: {response.headers}")
    print(f"GET Response Body:\n{repr(response.text)}")
except Exception as e:
    import traceback
    traceback.print_exc()

print("\n2. Sending POST /api/sso/auth/login...")
try:
    # First get session cookies from a successful or even failing request
    session_cookie = None
    response = client.get("/api/sso/oidc/authorize", params=params)
    cookies = response.cookies
    print(f"Acquired Cookies: {cookies.get_dict()}")

    login_payload = {
        **params,
        "email": "bkryksl@gmail.com",
        "password": "Password123"
    }
    response_login = client.post("/api/sso/auth/login", json=login_payload, cookies=cookies)
    print(f"POST Response Status: {response_login.status_code}")
    print(f"POST Response Body:\n{repr(response_login.text)}")
except Exception as e:
    import traceback
    traceback.print_exc()
