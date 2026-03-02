import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_llm(goal):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Create a step-by-step plan to achieve: {goal}"}],
    )
    return response.choices[0].message.content

def run_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com")
        title = page.title()
        browser.close()
        return title

def run_agent(goal):
    print("🧠 Planning...\n")
    plan = ask_llm(goal)
    print(plan)

    print("\n⚙️ Executing browser action...\n")
    result = run_browser()

    print("\n✅ Result:", result)

if __name__ == "__main__":
    run_agent("Open Google and report the title")