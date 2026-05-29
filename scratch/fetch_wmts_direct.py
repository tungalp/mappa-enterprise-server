import urllib.request
import urllib.parse
import sys

def test_capabilities():
    map_path = "/workspace/scratch/qgis-projects/8d66221d-d90b-4804-9200-82b6157b7543.qgs"
    url = f"http://qgis-server/ows/?MAP={urllib.parse.quote(map_path)}&SERVICE=WMTS&REQUEST=GetCapabilities"
    
    print(f"Sending direct HTTP GET to QGIS Server:\n{url}\n")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=120) as response:
            status = response.status
            content = response.read()
            print(f"HTTP Status: {status}")
            print(f"Content Length: {len(content)} bytes")
            print("\nResponse snippet (first 1000 chars):")
            print(content[:1000].decode('utf-8', errors='ignore'))
            
            # Check for WMTS capabilities elements
            if b"Capabilities" in content and b"Layer" in content:
                print("\nSUCCESS! Capabilities document is valid and contains layers!")
            else:
                print("\nWARNING: Response does not look like a valid WMTS capabilities XML!")
    except Exception as e:
        print(f"Error requesting Capabilities: {e}")

if __name__ == "__main__":
    test_capabilities()
