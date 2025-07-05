# This module provides functions to interact with the Spotify API 
from typing import List, Tuple
import logging
logger = logging.getLogger(__name__)
import requests


def create_playlist(user_id, access_token, playlist_name, description="Created by VibeAI", public=True):
    # user_id should be passed as an argument to this function
    # Create the playlist
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    payload = {
        "name": playlist_name,
        "description": description,
        "public": public
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def add_tracks_to_playlist(playlist_id, track_uris, access_token):
    logger.debug(f"🎵 Track URIs to be added: {track_uris}")
    if not track_uris:
        logger.warning("⚠️ No valid track URIs found. Skipping track addition.")
        return {"error": "No tracks to add."}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    payload = {
        "uris": track_uris
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        response_json = response.json()
    except ValueError:
        logger.error("❌ Could not decode Spotify's response as JSON. Logged above.")
        return {"error": "Invalid JSON response from Spotify"}

    if response.status_code != 201:
        logger.error(f"❌ Spotify API returned status {response.status_code}: {response_json}")
        return {"error": f"Spotify API error: {response_json}"}

    logger.info(f"✅ Successfully added tracks to playlist {playlist_id}")
    return response_json

def get_user_top_tracks(access_token, limit=10):
    url = f"https://api.spotify.com/v1/me/top/tracks?limit={limit}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_liked_songs(access_token, limit=50, offset=0):
    url = f"https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def extract_song_info_from_liked_tracks(response_json):
    songs = []
    items = response_json.get("items", [])
    for item in items:
        track = item.get("track", {})
        name = track.get("name", "Unknown Track")
        artists = track.get("artists", [])
        artist_name = artists[0]["name"] if artists else "Unknown Artist"
        songs.append(f"{name} by {artist_name}")
    return songs


def search_songs_on_spotify(songs: List[Tuple[str, str]], access_token: str) -> List[str]:
    """
    Searches for songs on Spotify and returns a list of track URIs.
    """
    track_uris = []
    headers = {"Authorization": f"Bearer {access_token}"}
    search_url = "https://api.spotify.com/v1/search"

    for song_name, artist_name in songs:
        query = f"{song_name} {artist_name}"
        params = {"q": query, "type": "track", "limit": 1}

        response = requests.get(search_url, headers=headers, params=params)
        result = response.json()

        if response.status_code == 200 and result.get("tracks", {}).get("items"):
            track = result["tracks"]["items"][0]
            track_uris.append(track["uri"])
        else:
            logger.warning(f"🔍 Not found on Spotify: {song_name} by {artist_name}")

    return track_uris