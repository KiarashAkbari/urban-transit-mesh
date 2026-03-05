import asyncio
import json
import os
from playwright.async_api import async_playwright

async def scrape_mahsa_data():
    print("Starting Stealth Scrape of MahsaNet...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        print("Navigating to alert.mahsanet.com...")
        try:
            await page.goto("https://alert.mahsanet.com", wait_until="networkidle", timeout=30000)
            print("Page loaded. Waiting 5 seconds for map rendering...")
            await page.wait_for_timeout(5000)

            # This is the real DOM extraction logic we discussed
            extracted_data = await page.evaluate("""() => {
                const zones = [];
                
                // Look for standard mapbox/leaflet markers
                const markers = document.querySelectorAll('.leaflet-marker-icon, .mapboxgl-marker, [class*="marker"]');
                
                markers.forEach((marker, index) => {
                    let lat = null;
                    let lon = null;
                    let severity = 3;
                    let color = 'orange';
                    
                    // Attempt to extract coordinates from React fiber nodes
                    const reactPropsKey = Object.keys(marker).find(key => key.startsWith('__reactProps$'));
                    if (reactPropsKey) {
                        try {
                            const props = marker[reactPropsKey];
                            if (props.children && props.children.props && props.children.props.position) {
                                lat = props.children.props.position[0];
                                lon = props.children.props.position[1];
                            }
                        } catch (e) {}
                    }
                    
                    // If no exact coords, we log a warning but skip to keep data clean
                    if (!lat || !lon) return;

                    // Determine severity based on visuals
                    if (marker.innerHTML.includes('red') || marker.innerHTML.includes('critical') || marker.innerHTML.includes('strike')) {
                        color = 'red';
                        severity = 5;
                    }
                    
                    zones.push({
                        "zone_name": `Live Anomaly ${index + 1}`,
                        "lat": lat,
                        "lon": lon,
                        "radius_km": severity * 2,
                        "color": color,
                        "severity_index": severity
                    });
                });
                
                // Fallback if no markers are currently active on their site
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
            
            print(f"Extracted {len(extracted_data)} zones.")

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            json_path = os.path.join(data_dir, "active_zones.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=4)
                
            print(f"Data saved to {json_path}")

        except Exception as e:
            print(f"Scraping failed: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_mahsa_data())
