from fastapi import APIRouter, Query, Form
from pydantic import BaseModel
from utils.token import get_access_token
from utils.groq import get_user_music_history, build_prompt_with_history, build_prompt_without_history, call_groq_api
from utils.config import logger

router = APIRouter()

class GroqRequest(BaseModel):
    user_id: str
    vibe_prompt: str
    personalize: bool = True

@router.post("/groq-recommend-vibe")
def recommend_vibe_based_music(payload: GroqRequest):
    access_token = get_access_token(payload.user_id)
    
    if payload.personalize:
        combined_tracks = get_user_music_history(access_token)
        if combined_tracks:
            base_prompt = build_prompt_with_history(combined_tracks, payload.vibe_prompt)
        else:
            logger.warning("⚠️ No music history found. Building prompt using only vibe_prompt.")
            base_prompt = build_prompt_without_history(payload.vibe_prompt)
    else:
        base_prompt = build_prompt_without_history(payload.vibe_prompt)

    response = call_groq_api(base_prompt)

    return {"groq_recommendations": response.choices[0].message.content}