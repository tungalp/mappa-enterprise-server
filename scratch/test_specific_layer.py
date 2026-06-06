import requests

def test():
    base_url = "http://127.0.0.1:33108/api/desktop-mobile"
    login_url = f"{base_url}/api_keys/exchange_token"
    
    headers = {
        "Authorization": "Bearer pk_SlgGXHC2-p2sYHr3S3oXmT6IUBnDr",
        "Accept": "application/json"
    }
    r = requests.post(login_url, headers=headers, timeout=10.0)
    r.raise_for_status()
    token = r.json()["access_token"]
    
    auth_headers = {
        "Authorization": f"Bearer {token}",
        "X-Client-ID": "mappa-mobile-default-client",
        "Accept": "application/json"
    }
    
    layer_id = "076bb56a-7298-41ee-aa2c-735080fd76af"
    url = f"{base_url}/layers/{layer_id}/data-source?as_geojson=true"
    print(f"Requesting: {url}")
    resp = requests.get(url, headers=auth_headers, timeout=45.0)
    print("Status:", resp.status_code)
    print("Response:", resp.text)

if __name__ == "__main__":
    test()
