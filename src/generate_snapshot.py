import os
import asyncio
from datetime import datetime
import pytz
from playwright.async_api import async_playwright

async def capture_map_snapshot():
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_path = f"file://{os.path.join(base_dir, 'mesh_map_base.html')}"
    output_image = os.path.join(base_dir, "alert_map.png")

    # Generate current IRST timestamp
    tehran_tz = pytz.timezone('Asia/Tehran')
    current_time = datetime.now(tehran_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # Bilingual timestamp overlay
    timestamp_text = f"NATIONAL MESH STATUS | وضعیت شبکه ملی<br>VALID AS OF: {current_time} IRST"


    print(f"Opening map: {map_path}")

    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={'width': 1200, 'height': 800} # High-res size for Telegram
        )

        # Open the local HTML file and wait for the map tiles to load
        await page.goto(map_path, wait_until="networkidle")
        
        # Give Folium an extra second to finish rendering polygons
        await page.wait_for_timeout(2000)

        # Inject the massive timestamp directly into the DOM
        await page.evaluate(f"""
            const timestampDiv = document.createElement('div');
            timestampDiv.innerHTML = '{timestamp_text}';
            timestampDiv.style.position = 'absolute';
            timestampDiv.style.top = '20px';
            timestampDiv.style.left = '50%';
            timestampDiv.style.transform = 'translateX(-50%)';
            timestampDiv.style.zIndex = '9999';
            timestampDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            timestampDiv.style.color = 'yellow';
            timestampDiv.style.padding = '15px 30px';
            timestampDiv.style.fontSize = '32px';
            timestampDiv.style.fontWeight = 'bold';
            timestampDiv.style.border = '3px solid red';
            timestampDiv.style.borderRadius = '8px';
            timestampDiv.style.fontFamily = 'monospace';
            document.body.appendChild(timestampDiv);
        """)

        print(f"Taking snapshot...")
        await page.screenshot(path=output_image)
        await browser.close()
        
    print(f"Snapshot saved successfully: {output_image}")

if __name__ == "__main__":
    asyncio.run(capture_map_snapshot())
