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
    
    map_id = "8d66221d-d90b-4804-9200-82b6157b7543"
    url = f"{base_url}/layers/maps/{map_id}/data-sources"
    print(f"Requesting: {url}")
    resp = requests.get(url, headers=auth_headers, timeout=60.0)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        print(f"SUCCESS! Received data for {len(data)} layers.")
        for lyr_id, geojson in list(data.items())[:3]:
            features = geojson.get("features", [])
            print(f"  Layer ID: {lyr_id} | Features: {len(features)}")
    else:
        print("Response:", resp.text)

if __name__ == "__main__":
    test()
