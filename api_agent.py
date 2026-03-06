import os
import uuid
import json
import requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# -------------------------------
# CONFIG
# -------------------------------

DELIVERABLE_DIR = "deliverables"
PORTFOLIO_FILE = "portfolio.json"

os.makedirs(DELIVERABLE_DIR, exist_ok=True)

app.mount("/deliverables", StaticFiles(directory=DELIVERABLE_DIR), name="deliverables")

# Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# -------------------------------
# UTILITIES
# -------------------------------

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []

    try:
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_portfolio(data):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_to_portfolio(file_name, caption):
    portfolio = load_portfolio()

    portfolio.append({
        "url": f"/deliverables/{file_name}",
        "type": "image",
        "caption": caption,
        "created_at": datetime.utcnow().isoformat()
    })

    save_portfolio(portfolio)

# -------------------------------
# PROTOCOL ENDPOINTS
# -------------------------------

@app.get("/agent/profile")
def profile():
    return {
        "name": "Cinematic Image Architect",
        "description": "Generates cinematic AI images from ideas.",
        "avatar_url": "https://placehold.co/256x256",
        "capabilities": ["image_gen"]
    }


@app.get("/agent/services")
def services():
    return {
        "services": [
            {
                "id": "cinematic_image",
                "title": "Cinematic AI Image",
                "description": "Generate a cinematic AI image based on your idea.",
                "price_usd": 3.99,
                "category": "image_gen"
            }
        ]
    }


class ExecuteRequest(BaseModel):
    service_id: str
    brief: str
    params: dict | None = None


@app.post("/agent/execute")
def execute(req: ExecuteRequest):

    idea = req.brief

    # Step 1: Improve prompt
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an AI art prompt engineer."},
            {"role": "user", "content": f"Create a cinematic image prompt for: {idea}"}
        ]
    )

    prompt = response.choices[0].message.content

    # Step 2: Generate image
    image_url = f"https://image.pollinations.ai/prompt/{prompt}"

    img = requests.get(image_url)

    deliverable_id = str(uuid.uuid4())
    filename = f"{deliverable_id}.png"
    file_path = os.path.join(DELIVERABLE_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(img.content)

    # Step 3: Save to portfolio
    add_to_portfolio(filename, idea)

    return {
        "result": "success",
        "deliverable_url": f"/deliverables/{filename}"
    }


@app.get("/agent/portfolio")
def portfolio():
    return {
        "works": load_portfolio()
    }
