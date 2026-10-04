import os
import time
from playwright.sync_api import sync_playwright

def capture_screenshots(base_url="http://127.0.0.1:8050", output_dir="docs/screenshots"):
    os.makedirs(output_dir, exist_ok=True)
    
    pages = [
        {"name": "overview", "path": "/"},
        {"name": "trends", "path": "/trends"},
        {"name": "map", "path": "/map"},
        {"name": "districts", "path": "/districts"},
        {"name": "prediction", "path": "/prediction"},
        {"name": "model_comparison", "path": "/model-comparison"},
        {"name": "about", "path": "/about"}
    ]
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception:
            print("Installing Playwright Chromium browser...")
            os.system("python -m playwright install chromium")
            browser = p.chromium.launch(headless=True)
            
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        for item in pages:
            url = f"{base_url}{item['path']}"
            print(f"Navigating to {url}...")
            page.goto(url, wait_until="networkidle")
            time.sleep(2)  # Allow charts to render completely
            
            output_file = os.path.join(output_dir, f"{item['name']}.png")
            page.screenshot(path=output_file, full_page=True)
            print(f"Captured screenshot: {output_file}")
            
        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    capture_screenshots()
