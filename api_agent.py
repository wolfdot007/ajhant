import os
import uuid
import json
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# ---- GROQ FREE LLM CLIENT ----
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- Open Protocol Endpoints ----------

@app.get("/agent/profile")
def profile():
    return {
        "name": "Kling Cinematic Prompt Architect",
        "description": "Transforms rough ideas into cinematic Kling-ready prompts optimized for short-form video.",
        "avatar_url": "https://yourdomain.com/avatar.png",
        "capabilities": [
            "cinematic video prompt engineering",
            "lighting architecture",
            "camera choreography",
            "viral short-form optimization"
        ]
    }


@app.get("/agent/services")
def services():
    return {
        "services": [
            {"id": "cinematic_basic", "title": "Cinematic Kling Prompt", "price_usd": 5, "category": "video"},
            {"id": "cinematic_pro", "title": "Cinematic Prompt + Shot Breakdown", "price_usd": 12, "category": "video"},
            {"id": "viral_bundle", "title": "Cinematic Prompt + Viral Strategy", "price_usd": 18, "category": "growth"}
        ]
    }


class ExecuteRequest(BaseModel):
    service_id: str
    input: dict


@app.post("/agent/execute")
def execute(req: ExecuteRequest):
    idea = req.input.get("idea", "")
    mood = req.input.get("mood", "cinematic")
    platform = req.input.get("platform", "short-form")

    system_prompt = """
You are a professional cinematic AI video prompt engineer.
Generate highly optimized Kling-ready prompts with detailed camera,
lighting, motion, and negative prompts.
Output structured sections clearly.
"""

    user_prompt = f"""
Idea: {idea}
Mood: {mood}
Platform: {platform}
Generate a cinematic Kling-ready structured prompt.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # FREE GROQ MODEL
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    output_text = response.choices[0].message.content

    deliverable_id = str(uuid.uuid4())
    os.makedirs("deliverables", exist_ok=True)
    file_path = f"deliverables/{deliverable_id}.json"

    with open(file_path, "w") as f:
        json.dump({"content": output_text}, f)

    return {
        "result": "success",
        "deliverable_url": f"/deliverables/{deliverable_id}.json"
    }


@app.get("/agent/portfolio")
def portfolio():
    return {
        "works": []
    }