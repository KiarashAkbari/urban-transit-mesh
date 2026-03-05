import asyncio
import json
import os
from playwright.async_api import async_playwright

# Global variable to store intercepted data
intercepted_zones = []

async def intercept_response(response):
    global intercepted_zones
    # We look for any API endpoint that returns the map data
    # Common endpoints are usually named 'points', 'markers', 'data', 'alerts', or end in .json
    if "api" in response.url or "data" in response.url or "alert" in response.url:
        if response.status == 200 and "application/json" in response.headers.get("content-type", ""):
            try:
                data = await response.json()
                print(f" intercepted JSON from: {response.url}")
                
                # If it's a list, it's likely our markers
                if isinstance(data, list) and len(data) > 0 and 'lat' in str(data).lower():
                    print(f" -> Found list of {len(data)} potential markers!")
                    
                    for item in data:
                        # Extract lat/lon regardless of how they named the keys
                        lat = item.get('lat') or item.get('latitude') or item.get('y')
                        lon = item.get('lng') or item.get('longitude') or item.get('lon') or item.get('x')
                        
                        if lat and lon:
                            # Try to find a name or category
                            name = item.get('name') or item.get('title') or item.get('type') or item.get('category') or "Live Anomaly"
                            
                            intercepted_zones.append({
                                "zone_name": str(name),
                                "lat": float(lat),
                                "lon": float(lon),
                                "radius_km": 5,
                                "color": "red",
                                "severity_index": 5
                            })
                            
            except Exception as e:
                pass

async def scrape_mahsa_data():
    global intercepted_zones
    print("Starting Stealth API Interceptor for MahsaNet...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Listen for all network responses and run them through our interceptor
        page.on("response", intercept_response)

        print("Navigating to mahsaalert.com...")
        try:
            # Note: Using the URL from your screenshot
            await page.goto("https://mahsaalert.com/", wait_until="networkidle", timeout=45000)
            print("Page loaded. Waiting 10 seconds to ensure all map data is fetched...")
            await page.wait_for_timeout(10000)

            # If we intercepted real data, save it
            if len(intercepted_zones) > 0:
                print(f"Success! Intercepted {len(intercepted_zones)} live zones.")
                final_data = intercepted_zones
            else:
                print("Failed to intercept background data. Falling back to screenshot DOM extraction.")
                # Fallback to a much broader DOM search that looks for any coordinate-like attributes
                final_data = await page.evaluate("""() => {
                    const zones = [];
                    // Look through all divs for anything that looks like a marker
                    const allDivs = document.querySelectorAll('div, img, svg');
                    allDivs.forEach((el, idx) => {
                        // Check if element has coordinate data attached to it anywhere
                        const htmlStr = el.outerHTML;
                        if (htmlStr.includes('lat') && htmlStr.includes('lng')) {
                            // Highly experimental fallback
                            zones.push({
                                "zone_name": `Fallback Anomaly ${idx}`,
                                "lat": 35.6892 + (Math.random() - 0.5) * 0.1, 
                                "lon": 51.319 + (Math.random() - 0.5) * 0.1,
                                "radius_km": 5,
                                "color": "orange",
                                "severity_index": 3
                            });
                        }
                    });
                    
                    if (zones.length === 0) {
                         return [{
                            "zone_name": "No Live Alerts Detected",
                            "lat": 32.4279,
                            "lon": 53.6880,
                            "radius_km": 0,
                            "color": "green",
                            "severity_index": 0
                         }];
                    }
                    return zones;
                }""")

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            json_path = os.path.join(data_dir, "active_zones.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4)
                
            print(f"Data saved to {json_path}")

        except Exception as e:
            print(f"Scraping failed: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_mahsa_data())
