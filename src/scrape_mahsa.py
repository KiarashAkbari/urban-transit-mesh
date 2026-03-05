import asyncio
import json
import os
from playwright.async_api import async_playwright

async def scrape_mahsa_data():
    print("Starting Stealth Scrape of MahsaNet...")
    
    async with async_playwright() as p:
        # Using stealth settings similar to CLONE-1
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        print("Navigating to alert.mahsanet.com...")
        try:
            # Wait for network to be idle so the map data fully loads
            await page.goto("https://alert.mahsanet.com", wait_until="networkidle", timeout=30000)
            print("Page loaded. Waiting 5 seconds for map rendering...")
            await page.wait_for_timeout(5000)

            # This is where we inject JS to extract the data.
            # Depending on how they render (Leaflet/Mapbox), we look for specific DOM elements.
            # For now, we will extract raw text alerts from the DOM as a proof of concept.
            
            extracted_data = await page.evaluate("""() => {
                // This is a placeholder extraction. We need to inspect their exact DOM classes.
                // For a real map, we'd extract from window.map or Leaflet layers.
                return [
                    {
                        "zone_name": "Scraped Zone (Placeholder)",
                        "lat": 35.6892,
                        "lon": 51.3190,
                        "radius_km": 8,
                        "color": "red",
                        "severity_index": 5
                    }
                ];
            }""")
            
            print(f"Extracted {len(extracted_data)} zones.")

            # Save to JSON
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
