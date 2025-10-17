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

class CreatePlaylistRequest(BaseModel):
    songs: List[dict]
    playlist_name: str
    user_id: Optional[str] = None

@router.post("/create-spotify-playlist")
def create_spotify_playlist(data: CreatePlaylistRequest) -> JSONResponse:
    """
    Create a Spotify playlist from search results (copied from v2 frontend)
    """
    try:
        songs = data.songs
        playlist_name = data.playlist_name or 'VibeAI Search Results'
        
        if not songs:
            return JSONResponse(status_code=400, content={"success": False, "error": "No songs provided"})
        
        # Extract Spotify URIs from songs
        track_uris = []
        invalid_songs = []
        
        for song in songs:
            if song.get('spotify_uri') and song.get('spotify_uri') != 'spotify:track:':
                track_uris.append(song['spotify_uri'])
            elif song.get('spotify_id'):
                spotify_id = song['spotify_id']
                # Clean and validate Spotify ID
                if spotify_id and isinstance(spotify_id, str):
                    spotify_id = spotify_id.strip()
                    # Validate Spotify ID format (22 characters, alphanumeric)
                    if len(spotify_id) == 22 and spotify_id.isalnum():
                        track_uris.append(f"spotify:track:{spotify_id}")
                    else:
                        invalid_songs.append({
                            'id': spotify_id,
                            'title': song.get('title', 'Unknown'),
                            'artist': song.get('artist', 'Unknown'),
                            'reason': f'Invalid format (length: {len(spotify_id)})'
                        })
                else:
                    invalid_songs.append({
                        'id': spotify_id,
                        'title': song.get('title', 'Unknown'),
                        'artist': song.get('artist', 'Unknown'),
                        'reason': 'Empty or invalid type'
                    })
            else:
                invalid_songs.append({
                    'id': None,
                    'title': song.get('title', 'Unknown'),
                    'artist': song.get('artist', 'Unknown'),
                    'reason': 'No Spotify ID or URI'
                })
        
        logger.info(f"🎵 Creating playlist with {len(track_uris)} valid tracks")
        if invalid_songs:
            logger.warning(f"⚠️ Skipped {len(invalid_songs)} invalid songs")
        
        if not track_uris:
            return JSONResponse(status_code=400, content={"success": False, "error": "No valid Spotify URIs found"})
        
        # Get service account token for anonymous use
        access_token = get_service_account_access_token()
        if not access_token:
            return JSONResponse(status_code=500, content={"success": False, "error": "Failed to get Spotify access token"})
        
        # Get the actual Spotify user ID for the service account
        user_response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code != 200:
            return JSONResponse(status_code=500, content={"success": False, "error": f"Failed to get user info: {user_response.json()}"})
        
        service_user_id = user_response.json()['id']
        
        # Create playlist (using service account user ID)
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        unique_playlist_name = f"{playlist_name} - {unique_id}"
        
        playlist = create_playlist(
            user_id=service_user_id,
            access_token=access_token,
            playlist_name=unique_playlist_name,
            description=f"Created by VibeAI - {len(track_uris)} songs",
            public=True
        )
        
        if 'error' in playlist:
            return JSONResponse(status_code=500, content={"success": False, "error": f"Failed to create playlist: {playlist['error']}"})
        
        playlist_id = playlist["id"]
        playlist_url = playlist["external_urls"]["spotify"]
        
        # Add tracks to playlist with retry logic
        logger.info(f"🎵 Adding {len(track_uris)} tracks to playlist")
        
        add_response = add_tracks_to_playlist(playlist_id, track_uris, access_token)
        
        if 'error' in add_response:
            error_details = add_response['error']
            if isinstance(error_details, dict) and 'message' in error_details:
                error_message = f"Spotify API error: {error_details}"
            else:
                error_message = f"Failed to add tracks: {error_details}"
            
            logger.error(f"❌ Error adding tracks: {error_message}")
            
            # If we have many tracks, try with fewer tracks to isolate the problematic ones
            if len(track_uris) > 5:
                logger.info(f"🔄 Retrying with first 5 tracks only...")
                retry_response = add_tracks_to_playlist(playlist_id, track_uris[:5], access_token)
                if 'error' not in retry_response:
                    logger.info(f"✅ Successfully added {len(track_uris[:5])} tracks (out of {len(track_uris)} requested)")
                    return JSONResponse(content={
                        "success": True,
                        "playlist_id": playlist_id,
                        "playlist_url": playlist_url,
                        "playlist_name": unique_playlist_name,
                        "tracks_added": len(track_uris[:5]),
                        "warning": f'Only {len(track_uris[:5])} tracks added due to API errors'
                    })
            
            return JSONResponse(status_code=500, content={"success": False, "error": error_message})
        
        # Success!
        logger.info(f"✅ Successfully created playlist with {len(track_uris)} tracks")
        return JSONResponse(content={
            "success": True,
            "playlist_id": playlist_id,
            "playlist_url": playlist_url,
            "playlist_name": unique_playlist_name,
            "tracks_added": len(track_uris)
        })
        
    except Exception as e:
        logger.error(f"❌ Error creating Spotify playlist: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": f"Failed to create playlist: {str(e)}"})
