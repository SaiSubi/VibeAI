from fastapi import APIRouter, Query, Form
from utils.token import get_access_token
from utils.groq import get_user_music_history, build_groq_prompt, call_groq_api
from utils.config import logger

router = APIRouter()

@router.post("/groq-recommend-vibe")
def recommend_vibe_based_music(vibe_prompt: str = Form(...), user_id: str = Query(...)):
    access_token = get_access_token(user_id)
    
    combined_tracks = get_user_music_history(access_token)
    if not combined_tracks:
        return {"error": "❌ No songs found to base recommendations on."}

    base_prompt = build_groq_prompt(combined_tracks, vibe_prompt)

    response = call_groq_api(base_prompt)

    return {"groq_recommendations": response.choices[0].message.content}