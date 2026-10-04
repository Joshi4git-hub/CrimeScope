import os
import time
from playwright.sync_api import sync_playwright

def test_slider_hover():
    output_file = "docs/screenshots/prediction_hover_test.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto("http://127.0.0.1:8050/prediction", wait_until="networkidle")
        time.sleep(2)
        
        # Hover over the slider handle knob
        handle = page.locator(".rc-slider-handle").first
        if handle.count() > 0:
            handle.hover()
            time.sleep(1)
            
        page.screenshot(path=output_file)
        browser.close()
        print(f"Captured hover test screenshot: {output_file}")

if __name__ == "__main__":
    test_slider_hover()
