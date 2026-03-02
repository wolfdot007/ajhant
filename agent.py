from playwright.sync_api import sync_playwright

def run_task(task):
    print(f"Task: {task}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com")
        print("Page title:", page.title())
        browser.close()

if __name__ == "__main__":
    run_task("Open Google and check title")
