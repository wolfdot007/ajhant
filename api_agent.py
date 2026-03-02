from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

def run_browser_task(task: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        title = page.title()
        browser.close()
        return {"task": task, "result": title}

@app.get("/")
def root():
    return {"status": "Agent is running"}

@app.post("/run-task")
def run_task(request: TaskRequest):
    output = run_browser_task(request.task)
    return output