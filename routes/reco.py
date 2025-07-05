from fastapi import APIRouter, Query, Form
from pydantic import BaseModel
from utils.token import get_access_token
from utils.groq import get_user_music_history, build_groq_prompt, call_groq_api
from utils.config import logger

router = APIRouter()

class GroqRequest(BaseModel):
    user_id: str
    vibe_prompt: str

@router.post("/groq-recommend-vibe")
def recommend_vibe_based_music(payload: GroqRequest):
    access_token = get_access_token(payload.user_id)
    
    combined_tracks = get_user_music_history(access_token)
    if not combined_tracks:
        return {"error": "❌ No songs found to base recommendations on."}

    base_prompt = build_groq_prompt(combined_tracks, payload.vibe_prompt)

    response = call_groq_api(base_prompt)

    return {"groq_recommendations": response.choices[0].message.content}