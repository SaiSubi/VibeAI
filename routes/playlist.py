import re
import requests
from fastapi import APIRouter, Body, Query
from fastapi.responses import JSONResponse
from typing import List, Tuple
from pydantic import BaseModel
from utils.token import get_access_token, get_service_account_access_token
from utils.spotify import create_playlist, add_tracks_to_playlist, search_songs_on_spotify
from utils.groq import extract_songs_from_groq_response
from utils.config import logger, VibeAI_userid

router = APIRouter()

class GroqToPlaylistRequest(BaseModel):
    groq_response: str
    user_id: str
    personalize: bool = True


@router.post("/groq-to-playlist")
def groq_to_playlist(data: GroqToPlaylistRequest) -> JSONResponse:
    """
    Accepts Groq's recommendation text and creates a playlist based on extracted songs.
    """
    access_token = (
        get_access_token(data.user_id)
        if data.personalize
        else get_service_account_access_token()
    )

    # Step 1: Extract (song, artist) pairs from Groq's response
    songs = extract_songs_from_groq_response(data.groq_response)
    if not songs:
        return JSONResponse(content={"error": "❌ No valid songs found in Groq response."})

    # Step 2: Search each song on Spotify and collect URIs
    track_uris = search_songs_on_spotify(songs, access_token)
    if not track_uris:
        return JSONResponse(content={"error": "❌ No matching Spotify tracks found."})

    # Step 3: Create new playlist (replacing old logic)
    user_id = data.user_id if data.personalize else VibeAI_userid
    playlist = create_playlist(
        user_id=user_id,
        access_token=access_token,
        playlist_name="Groq Vibe Recommendations",
        description="Songs recommended by Groq based on your vibes 💫",
        public=True
    )
    playlist_id = playlist["id"]
    playlist_url = playlist["external_urls"]["spotify"]

    # Step 4: Add tracks
    add_response = add_tracks_to_playlist(playlist_id, track_uris, access_token)

    return JSONResponse(content={
        "message": "🎶 Groq songs added to playlist!",
        "playlist_id": playlist_id,
        "playlist_url": playlist_url,
        "added_tracks": len(track_uris)
    })
