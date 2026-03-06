import requests
import json

def probe_endpoints():
    print("Starting MahsaNet API Probe from Cloud Runner...\n")
    
    # Common REST API and static data endpoints used in open-source crisis maps
    endpoints_to_test = [
        "https://api.mahsaalert.app/",
        "https://api.mahsaalert.app/v1/alerts",
        "https://api.mahsaalert.app/api/alerts",
        "https://api.mahsaalert.app/data/alerts.json",
        "https://api.mahsaalert.app/api/v1/incidents",
        "https://api.mahsaalert.app/api/map-data",
        "https://alert.mahsanet.com/data.json",
        "https://alert.mahsanet.com/alerts.json"
    ]

    for url in endpoints_to_test:
        print(f"Testing: {url}")
        try:
            # Using a standard browser User-Agent so we don't get blocked by Cloudflare
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            print(f" -> Status: {response.status_code}")
            
            if response.status_code == 200:
                print(" -> SUCCESS! Found an active endpoint.")
                try:
                    data = response.json()
                    print(" -> Data Structure Snippet:")
                    # Print just the first 300 characters to inspect the structure
                    print(json.dumps(data, ensure_ascii=False)[:300] + "...\n")
                except json.JSONDecodeError:
                    print(" -> Response is not JSON. Likely HTML.")
            print("-" * 50)
            
        except requests.exceptions.RequestException as e:
            print(f" -> Failed: {e}\n" + "-" * 50)

if __name__ == "__main__":
    probe_endpoints()
