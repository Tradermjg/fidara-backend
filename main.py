from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os, random

app = FastAPI(title="Fidara Stub API", version="1.0.0")

API_KEY = os.getenv("API_KEY", "fidara_secret_key")  # set same value in Render
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "6"))

class RecommendationRequest(BaseModel):
    user_id: str
    agent_profile: Dict[str, Any] = {}
    request_text: str
    top_k: Optional[int] = None

class RefineRequest(BaseModel):
    user_id: str
    agent_profile: Dict[str, Any] = {}
    base_recommendation_id: Optional[str] = None
    refine_text: str
    top_k: Optional[int] = None

class FeedbackRequest(BaseModel):
    user_id: str
    recommendation_id: Optional[str] = None
    item_index: int
    signal: str
    comment: Optional[str] = None
    agent_profile: Dict[str, Any] = {}

SAMPLE_ITEMS = [
    {"title": "Portable Espresso Maker", "subtitle": "Compact under $150",
     "rationale": "Matches value: budget + craftsmanship.",
     "source_link": "https://example.com/espresso",
     "tags": ["coffee","travel","budget"]},
    {"title": "Trail Running Shoes", "subtitle": "Neutral support, rugged outsole",
     "rationale": "Durable outdoor gear favored by similar users.",
     "source_link": "https://example.com/shoes",
     "tags": ["running","outdoors","durable"]},
    {"title": "Hi-Fi Starter Amp", "subtitle": "Clean 40 W per channel",
     "rationale": "Good for craftsmanship & audio fidelity.",
     "source_link": "https://example.com/amp",
     "tags": ["audio","hi-fi","craftsmanship"]},
    {"title": "Steel Drum Essentials", "subtitle": "Afro-Caribbean playlist",
     "rationale": "Aligns with island & jazz tastes.",
     "source_link": "https://example.com/playlist",
     "tags": ["music","island","jazz"]},
    {"title": "Compact Travel Tripod", "subtitle": "Lightweight but stable",
     "rationale": "Balances portability and quality.",
     "source_link": "https://example.com/tripod",
     "tags": ["photo","travel","quality"]},
    {"title": "Budget Pour-Over Kit", "subtitle": "Beginner friendly",
     "rationale": "Great price-to-flavor starter kit.",
     "source_link": "https://example.com/pourover",
     "tags": ["coffee","budget","beginner"]},
]

def _rank_by_keywords(items: List[dict], text: str, k: int) -> List[dict]:
    t = (text or "").lower()
    scored = []
    for it in items:
        keys = [it["title"].lower(), it["subtitle"].lower()] + it.get("tags", [])
        score = sum(1 for kw in keys if kw and str(kw).lower() in t)
        scored.append((score, random.random(), it))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [it for _,__,it in scored][:k]

def _require_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/recommendations")
def recommendations(data: RecommendationRequest, x_api_key: str = Header(...)):
    _require_key(x_api_key)
    k = data.top_k or TOP_K_DEFAULT
    items = _rank_by_keywords(SAMPLE_ITEMS, data.request_text, k)
    return {"items": items, "agent_profile": {**data.agent_profile, "last_stub_update": "now"}}

@app.post("/api/recommendations/refine")
def refine(data: RefineRequest, x_api_key: str = Header(...)):
    _require_key(x_api_key)
    k = data.top_k or TOP_K_DEFAULT
    items = _rank_by_keywords(SAMPLE_ITEMS, data.refine_text, k)
    return {"items": items, "agent_profile": {**data.agent_profile, "last_refine": "now"}}

@app.post("/api/feedback")
def feedback(data: FeedbackRequest, x_api_key: str = Header(...)):
    _require_key(x_api_key)
    ap = dict(data.agent_profile)
    ap["last_feedback"] = {"signal": data.signal}
    return {"agent_profile": ap}
