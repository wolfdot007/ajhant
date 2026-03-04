import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from fastapi import Header, HTTPException

app = FastAPI()

DELIVERABLE_DIR = "deliverables"
PORTFOLIO_FILE = "portfolio.json"

os.makedirs(DELIVERABLE_DIR, exist_ok=True)

if not os.path.exists(PORTFOLIO_FILE):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump({"works": []}, f)



client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)



class ExecuteRequest(BaseModel):
    service_id: str
    brief: str
    params: Dict[str, Any] = {}



def load_portfolio():
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)


def save_portfolio(data):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f)


def add_to_portfolio(deliverable_id: str, caption: str):
    portfolio = load_portfolio()

    portfolio["works"].append({
        "url": f"/deliverables/{deliverable_id}.json",
        "type": "video_prompt",
        "caption": caption,
        "created_at": datetime.utcnow().isoformat()
    })

    # keep last 10
    portfolio["works"] = portfolio["works"][-10:]

    save_portfolio(portfolio)



@app.get("/agent/profile")
def agent_profile():
    return {
        "name": "Kling Cinematic Prompt Architect",
        "description": "Transforms rough ideas into cinematic Kling-ready prompts optimized for short-form video.",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712027.png",
        "capabilities": [
            "cinematic video prompt engineering",
            "lighting architecture",
            "camera choreography",
            "viral short-form optimization"
        ]
    }


@app.get("/agent/services")
def agent_services():
    return {
        "services": [
            {
                "id": "cinematic_basic",
                "title": "Cinematic Kling Prompt",
                "description": "Professional cinematic prompt optimized for Kling video generation.",
                "price_usd": 5,
                "category": "video"
            },
            {
                "id": "cinematic_pro",
                "title": "Cinematic Prompt + Shot Breakdown",
                "description": "Advanced cinematic prompt including camera movements and shot design.",
                "price_usd": 12,
                "category": "video"
            },
            {
                "id": "viral_bundle",
                "title": "Cinematic Prompt + Viral Strategy",
                "description": "Cinematic prompt plus short-form growth strategy.",
                "price_usd": 18,
                "category": "growth"
            }
        ]
    }


@app.post("/agent/execute")
def agent_execute(req: ExecuteRequest, x_api_key: str = Header(None)):

    expected_key = os.getenv("ATELIER_API_KEY")
 
    if x_api_key and x_api_key != expected_key:
         raise HTTPException(status_code=401, detail="Unauthorized")

    idea = req.brief
    mood = req.params.get("mood", "cinematic")
    platform = req.params.get("platform", "short-form")

    system_prompt = """
You are a professional cinematic AI video prompt engineer.

Generate highly optimized Kling-ready prompts including:
- scene description
- camera choreography
- lighting design
- motion direction
- negative prompts

Structure the output clearly.
"""

    user_prompt = f"""
Idea: {idea}
Mood: {mood}
Platform: {platform}

Generate a cinematic Kling-ready structured prompt.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    output_text = response.choices[0].message.content

    deliverable_id = str(uuid.uuid4())
    file_path = f"{DELIVERABLE_DIR}/{deliverable_id}.json"

    with open(file_path, "w") as f:
        json.dump({"content": output_text}, f)

    add_to_portfolio(deliverable_id, idea)

    return {
        "result": "success",
        "deliverable_url": f"/deliverables/{deliverable_id}.json"
    }


@app.get("/agent/portfolio")
def agent_portfolio():
    return load_portfolio()

app.mount("/deliverables", StaticFiles(directory=DELIVERABLE_DIR), name="deliverables")