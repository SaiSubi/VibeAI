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


def find_existing_playlist(user_id, access_token, playlist_name):
    """
    Search for an existing playlist with the given name for the user.
    Returns the playlist object if found, None otherwise.
    """
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            playlists = response.json().get("items", [])
            for playlist in playlists:
                if playlist.get("name") == playlist_name:
                    logger.info(f"✅ Found existing playlist: {playlist_name}")
                    return playlist
        else:
            logger.error(f"❌ Failed to fetch playlists: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error searching for existing playlist: {e}")
    
    return None


def clear_playlist_tracks(playlist_id, access_token):
    """
    Remove all tracks from a playlist.
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # First, get all tracks in the playlist
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tracks_data = response.json()
            track_uris = [track["track"]["uri"] for track in tracks_data.get("items", [])]
            
            if track_uris:
                # Remove all tracks
                payload = {"tracks": [{"uri": uri} for uri in track_uris]}
                delete_response = requests.delete(url, json=payload, headers=headers)
                if delete_response.status_code == 200:
                    logger.info(f"✅ Cleared {len(track_uris)} tracks from playlist {playlist_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to clear playlist: {delete_response.status_code}")
            else:
                logger.info(f"✅ Playlist {playlist_id} is already empty")
                return True
        else:
            logger.error(f"❌ Failed to get playlist tracks: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error clearing playlist: {e}")
    
    return False


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
    try:
        return response.json().get("items", [])
    except ValueError:
        logger.error("❌ Could not decode top tracks response.")
        return []

def get_liked_songs(access_token, limit=50, offset=0):
    url = f"https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    try:
        return response.json().get("items", [])
    except ValueError:
        logger.error("❌ Could not decode liked songs response.")
        return []

def extract_song_info_from_liked_tracks(tracks):
    songs = []
    for track in tracks:
        name = track.get("name", "Unknown Track")
        artists = track.get("artists", [])
        artist_name = artists[0]["name"] if artists else "Unknown Artist"
        songs.append(f"{name} by {artist_name}")
    return songs


def search_songs_on_spotify(songs: List[Tuple[str, str]], access_token: str) -> List[str]:
    """
    Searches for songs on Spotify using song and artist pairs and returns a list of track URIs.
    """
    track_uris = []
    headers = {"Authorization": f"Bearer {access_token}"}
    search_url = "https://api.spotify.com/v1/search"

    for song_name, artist_name in songs:
        query_string = f"{song_name} {artist_name}"
        logger.info(f"🔍 Searching Spotify for: {query_string}")
        params = {"q": query_string, "type": "track", "limit": 1}
        logger.info(f"🔍 Querying Spotify with params: {params}")
        response = requests.get(search_url, headers=headers, params=params)
        logger.info(f"📡 Spotify response status: {response.status_code}")
        logger.info(f"📄 Spotify response body: {response.text[:500]}")
        try:
            result = response.json()
        except ValueError:
            logger.error("❌ Failed to decode Spotify search response.")
            continue

        if response.status_code == 200 and result.get("tracks", {}).get("items"):
            track = result["tracks"]["items"][0]
            track_uris.append(track["uri"])
        else:
            logger.warning(f"🔍 Not found on Spotify for query: {query_string}")

    return track_uris