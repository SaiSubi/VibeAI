import re
import requests
from fastapi import APIRouter, Body, Query
from fastapi.responses import JSONResponse
from typing import Optional,List, Tuple
from pydantic import BaseModel
from utils.token import get_access_token, get_service_account_access_token
from utils.spotify import create_playlist, add_tracks_to_playlist, search_songs_on_spotify, find_existing_playlist, clear_playlist_tracks
from utils.groq import extract_songs_from_groq_response
from utils.config import logger, VibeAI_userid

router = APIRouter()

class GroqToPlaylistRequest(BaseModel):
    groq_response: str
    user_id: Optional[str] = None
    personalize: bool = True


@router.post("/groq-to-playlist")
def groq_to_playlist(data: GroqToPlaylistRequest) -> JSONResponse:
    """
    Accepts Groq's recommendation text and creates a playlist based on extracted songs.
    """
    if data.personalize:
        if not data.user_id:
            return JSONResponse(status_code=400, content={"error": "Missing user_id for personalized playlist."})
        access_token = get_access_token(data.user_id)
    else:
        access_token = get_service_account_access_token()

    # Step 1: Extract (song, artist) pairs from Groq's response
    songs = extract_songs_from_groq_response(data.groq_response)
    if not songs:
        return JSONResponse(content={"error": "❌ No valid songs found in Groq response."})

    # Step 2: Search each song on Spotify and collect URIs
    track_uris = search_songs_on_spotify(songs, access_token)
    if not track_uris:
        return JSONResponse(content={"error": "❌ No matching Spotify tracks found."})

    # Step 3: Handle playlist creation based on mode
    user_id = data.user_id if data.personalize else VibeAI_userid
    playlist_name = "VibeAI"
    playlist_description = "Songs recommended by VibeAI based on your vibes 💫"
    
    if data.personalize:
        # Personalized mode: Try to find existing playlist and reuse it
        existing_playlist = find_existing_playlist(user_id, access_token, playlist_name)
        
        if existing_playlist:
            # Found existing playlist, clear it and repopulate
            playlist_id = existing_playlist["id"]
            playlist_url = existing_playlist["external_urls"]["spotify"]
            
            # Clear existing tracks
            if clear_playlist_tracks(playlist_id, access_token):
                logger.info(f"✅ Reusing existing playlist: {playlist_name}")
            else:
                return JSONResponse(content={"error": "❌ Failed to clear existing playlist tracks."})
        else:
            # Create new playlist
            playlist = create_playlist(
                user_id=user_id,
                access_token=access_token,
                playlist_name=playlist_name,
                description=playlist_description,
                public=True
            )
            playlist_id = playlist["id"]
            playlist_url = playlist["external_urls"]["spotify"]
            logger.info(f"✅ Created new personalized playlist: {playlist_name}")
    else:
        # General mode: Always create a new playlist with unique identifier
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        unique_playlist_name = f"{playlist_name} - {unique_id}"
        
        playlist = create_playlist(
            user_id=user_id,
            access_token=access_token,
            playlist_name=unique_playlist_name,
            description=playlist_description,
            public=True
        )
        playlist_id = playlist["id"]
        playlist_url = playlist["external_urls"]["spotify"]
        logger.info(f"✅ Created new general playlist: {unique_playlist_name}")

    # Step 4: Add tracks
    add_response = add_tracks_to_playlist(playlist_id, track_uris, access_token)

    return JSONResponse(content={
        "message": "🎶 VibeAI songs added to playlist!",
        "playlist_id": playlist_id,
        "playlist_url": playlist_url,
        "added_tracks": len(track_uris)
    })
