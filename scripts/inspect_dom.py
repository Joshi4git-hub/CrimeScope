import time
from playwright.sync_api import sync_playwright

def inspect_slider_dom():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8050/prediction")
        time.sleep(2)
        
        # Get outer HTML of the container containing pred-hour-slider
        slider_html = page.eval_on_selector("#pred-hour-slider", "el => el.parentElement.outerHTML")
        print("SLIDER PARENT HTML:")
        print(slider_html)
        
        browser.close()

if __name__ == "__main__":
    inspect_slider_dom()
