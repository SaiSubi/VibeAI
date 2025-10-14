from fastapi import APIRouter, Query, Form
from pydantic import BaseModel
from utils.token import get_access_token
from utils.groq import get_user_music_history, build_prompt_with_history, build_prompt_without_history, call_groq_api
from utils.config import logger
from typing import Optional
import sys
import os

# Add v2 directory to path for agentic search
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "v2"))
from simplified_agentic_search import agentic_song_search

router = APIRouter()

class GroqRequest(BaseModel):
    user_id: Optional[str] = None
    vibe_prompt: str
    personalize: bool = True

class AgenticSearchRequest(BaseModel):
    query: str
    max_results: int = 20

@router.post("/groq-recommend-vibe")
def recommend_vibe_based_music(payload: GroqRequest):
    
    if payload.personalize:
        if not payload.user_id:
            raise ValueError("❌ user_id is required for personalized requests.")

        access_token = get_access_token(payload.user_id)
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

@router.post("/agentic-search")
def agentic_search_endpoint(payload: AgenticSearchRequest):
    """
    Agentic AI song search endpoint using multi-agent system.
    
    Args:
        payload: Contains query and max_results
        
    Returns:
        Dictionary with songs, metadata, and search information
    """
    try:
        logger.info(f"🎵 Agentic search request: '{payload.query}' (max_results: {payload.max_results})")
        
        # Call the agentic search system
        result = agentic_song_search(payload.query, payload.max_results)
        
        logger.info(f"✅ Agentic search completed: {result['total_selected']} songs found using {result['search_method']} method")
        
        return {
            "success": True,
            "query": payload.query,
            "query_interpretation": result["query_interpretation"],
            "search_method": result["search_method"],
            "total_candidates": result["total_candidates"],
            "total_selected": result["total_selected"],
            "selection_reasoning": result["selection_reasoning"],
            "enriched_query": result["enriched_query"],
            "songs": result["songs"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error in agentic search: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": payload.query,
            "songs": []
        }