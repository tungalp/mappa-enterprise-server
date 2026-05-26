import requests

# Parameters from user's URL
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

session = requests.Session()

# 1. GET /authorize to establish session
print("Establishing session via GET /authorize...")
auth_url = "http://localhost:33100/api/sso/oidc/authorize"
res = session.get(auth_url, params=params)
print(f"GET /authorize response status: {res.status_code}")
print(f"Session cookies: {session.cookies.get_dict()}")

# 2. POST /auth/login with credentials
login_url = "http://localhost:33100/api/sso/auth/login"
login_payload = {
    **params,
    "email": "bkryksl@gmail.com",
    "password": "Password123"
}

print("\nSubmitting login credentials...")
res_login = session.post(login_url, json=login_payload)
print(f"POST /login response status: {res_login.status_code}")
print(f"Response Content:\n{res_login.text}")
