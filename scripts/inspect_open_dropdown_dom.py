import time
from playwright.sync_api import sync_playwright

def inspect_open_dropdown():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8050/prediction")
        time.sleep(2)
        
        # Click on the Day of Week dropdown control to open it
        dropdown = page.locator("#pred-day-dropdown").first
        dropdown.click()
        time.sleep(1)
        
        # Print the entire page body HTML or search for open dropdown menus
        menu_html = page.eval_on_selector_all(
            "div[class*='menu'], div[class*='Menu'], div[class*='select'], div[role='listbox'], div[role='option'], div[class*='dropdown']",
            "elements => elements.map(e => e.outerHTML).join('\\n---\\n')"
        )
        print("OPEN DROPDOWN DOM ELEMENTS:")
        print(menu_html[:4000])
        
        browser.close()

if __name__ == "__main__":
    inspect_open_dropdown()
