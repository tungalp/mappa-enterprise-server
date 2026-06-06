import requests
import psycopg2

def test_endpoints():
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5454,
        dbname="mapa_test",
        user="postgres",
        password="postgres"
    )
    
    cursor = conn.cursor()
    # Query only layers with types: .kml, .kmz, .gdb.zip
    cursor.execute("""
        SELECT l.id, l.name, l.type, l.url_path 
        FROM desktop_mobile.layer l 
        WHERE l.type IN ('.kml', '.kmz', '.gdb.zip') OR l.url_path LIKE '%.gdb.zip%';
    """)
    layers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Found {len(layers)} target layers to test in database.")
    
    base_url = "http://127.0.0.1:33108/api/desktop-mobile"
    login_url = f"{base_url}/api_keys/exchange_token"
    print(f"Acquiring JWT token from {login_url}...")
    
    try:
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
        print("Successfully acquired JWT token!")
    except Exception as e:
        print(f"Failed to acquire token: {e}")
        return

    tested_types = set()
    for l_id, l_name, l_type, l_url in layers:
        clean_type = l_type.lower()
        if clean_type in tested_types:
            continue
        tested_types.add(clean_type)
        
        print(f"\n------------------------------------------")
        print(f"Testing Layer: {l_name} ({l_type})")
        print(f"ID: {l_id}")
        print(f"S3 Path: {l_url}")
        
        url = f"{base_url}/layers/{l_id}/data-source?as_geojson=true"
        print(f"Fetching from: {url}")
        
        try:
            resp = requests.get(url, headers=auth_headers, timeout=45.0)
            if resp.status_code == 200:
                geojson = resp.json()
                features = geojson.get("features", [])
                print(f"SUCCESS! Status 200. Converted to GeoJSON successfully!")
                print(f"Parsed Feature Count: {len(features)}")
                if features:
                    print("Sample feature properties:", list(features[0].get("properties", {}).keys())[:5])
            else:
                print(f"FAILED! Status: {resp.status_code}")
                print(f"Detail: {resp.text[:300]}")
        except Exception as e:
            print(f"Error during API call: {e}")

if __name__ == "__main__":
    test_endpoints()
