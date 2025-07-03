# This module provides functions to interact with the Spotify API 

import requests


def create_playlist(access_token, playlist_name, description="Created by VibeAI", public=True):
    # Fetch the user's Spotify ID from their access token
    user_info = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if user_info.status_code != 200:
        return {"error": "Failed to fetch user profile"}

    user_id = user_info.json()["id"]

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
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    payload = {
        "uris": track_uris
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

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