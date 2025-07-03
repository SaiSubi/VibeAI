# main.py

# ──────────────────────────────────────────────
# 🧱 Imports and Setup
# ──────────────────────────────────────────────
import os
import urllib.parse
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi import Body
from fastapi.responses import RedirectResponse
from openai import OpenAI
import json
import base64
from fastapi.middleware.cors import CORSMiddleware

from utils.spotify import create_playlist, add_tracks_to_playlist

# Placeholder for future user-based token storage
def get_tokens_for_user(user_id):
    raise NotImplementedError("User-based token storage not yet implemented.")


# ──────────────────────────────────────────────
# 🔐 Load Environment Variables
# ──────────────────────────────────────────────
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SPOTIFY_TEST_TOKEN = os.getenv("SPOTIFY_TEST_TOKEN")  # For quick testing

# ──────────────────────────────────────────────
# 🚀 FastAPI App Init
# ──────────────────────────────────────────────
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_access_token(user_id=None):
    if user_id:
        # Placeholder: Replace with actual DB or session storage fetch
        return get_tokens_for_user(user_id)["access_token"]
    else:
        with open("token.json", "r") as f:
            token_data = json.load(f)
        return token_data["access_token"]

def get_refresh_token(user_id=None):
    if user_id:
        # Placeholder: Replace with actual DB or session storage fetch
        return get_tokens_for_user(user_id)["refresh_token"]
    else:
        with open("token.json", "r") as f:
            token_data = json.load(f)
        return token_data["refresh_token"]
# ──────────────────────────────────────────────
# 🌐 Basic Health Check Route
# ──────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "VibeAI backend is live!"}

# ──────────────────────────────────────────────
# 🎧 Spotify Login Route
# ──────────────────────────────────────────────
@app.get("/login")
def login():
    scopes = "user-library-read playlist-modify-public user-top-read"
    auth_url = "https://accounts.spotify.com/authorize"

    query_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scopes,
    }

    # Redirect user to Spotify's login screen
    url = f"{auth_url}?{urllib.parse.urlencode(query_params)}"
    return RedirectResponse(url)

# ──────────────────────────────────────────────
# 🔁 Spotify Callback: Get Access + Refresh Token
# ──────────────────────────────────────────────
@app.get("/callback")
def callback(request: Request, code: str):
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        },
        headers={
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if response.status_code != 200:
        return {"error": response.json()}

    token_data = response.json()
    with open("token.json", "w") as f:
        json.dump(token_data, f, indent=4)

    # Set refresh token in cookie
    redirect = RedirectResponse(url="http://localhost:5173/home")  # Or wherever your frontend home is
    redirect.set_cookie(key="refresh_token", value=token_data["refresh_token"], httponly=True)

    return redirect

# ──────────────────────────────────────────────
# 🙋‍♂️ Get Current User's Spotify Profile (TEMP)
# ──────────────────────────────────────────────
@app.get("/me")
def get_user_profile():
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if response.status_code == 401:
        return {"error": "Access token expired or invalid. Please re-authenticate."}

    return response.json()

# ──────────────────────────────────────────────
# 🧠 Groq LLM Test Route
# ──────────────────────────────────────────────
@app.get("/groq-test")
def test_groq():
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are 3 good songs for someone feeling nostalgic but happy?"}
        ]
    )

    return response.choices[0].message.content


@app.get("/create-test-playlist")
def make_test_playlist():
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Get current user's profile info
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())  # 👈 this helps us debug

    user_profile = response.json()
    user_id = user_profile["id"]  # This is the line that throws KeyError if 'id' is missing

    # Step 2: Create a new playlist
    playlist_data = {
        "name": "VibeAI Test Playlist",
        "description": "Generated by VibeAI backend.",
        "public": True
    }

    playlist_response = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json=playlist_data
    )

    playlist = playlist_response.json()
    print("Playlist creation response:", playlist)

    playlist_id = playlist["id"]

    return {"message": "Playlist created!", "playlist_id": playlist_id}

from pydantic import BaseModel
from typing import List

class TrackRequest(BaseModel):
    playlist_id: str
    track_uris: List[str]

@app.post("/add-tracks")
def add_tracks_to_playlist_route(payload: TrackRequest):
    access_token = get_access_token()
    return add_tracks_to_playlist(
        playlist_id=payload.playlist_id,
        track_uris=payload.track_uris,
        access_token=access_token
    )
from utils.spotify import get_user_top_tracks

@app.get("/top-tracks")
def fetch_top_tracks():
    access_token = get_access_token()
    top_tracks = get_user_top_tracks(access_token)
    return top_tracks

from utils.spotify import get_liked_songs

from fastapi import Query
from utils.spotify import extract_song_info_from_liked_tracks

@app.get("/liked-songs")
def liked_songs():
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        "https://api.spotify.com/v1/me/tracks?limit=20",
        headers=headers
    )

    if response.status_code != 200:
        return {"error": "Failed to fetch liked songs"}

    liked_songs_data = response.json()
    song_descriptions = extract_song_info_from_liked_tracks(liked_songs_data)

    return {"songs": song_descriptions}



class SongList(BaseModel):
    songs: list[str]

@app.post("/groq-recommend")
def recommend_songs_from_groq(payload: SongList):
    song_list = payload.songs

    prompt = f"""
    These are songs I love:
    {chr(10).join(song_list)}

    Please suggest 5 more songs I might like, with a similar emotional or musical vibe. Include the song name and artist.
    """

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful music recommender assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"groq_recommendations": response.choices[0].message.content}

import re

@app.post("/groq-to-playlist")
def groq_to_playlist(
    groq_response: str = Body(...)
):
    access_token = get_access_token()

    # Step 1: Extract (song, artist) pairs from Groq's response
    lines = groq_response.split("\n")
    songs = []

    for line in lines:
        # Match lines like: 1. **Bulleya** by Arijit Singh - ...
        match = re.match(r"\d+\.\s+\*\*(.+?)\*\* by (.+?)\s*(?:-|$)", line.strip())
        if match:
            song_name, artist_name = match.groups()
            songs.append((song_name.strip(), artist_name.strip()))

    if not songs:
        return {"error": "❌ No valid songs found in Groq response."}

    # Step 2: Search each song on Spotify and collect URIs
    track_uris = []
    headers = {"Authorization": f"Bearer {access_token}"}
    search_url = "https://api.spotify.com/v1/search"

    for song_name, artist_name in songs:
        query = f"{song_name} artist:{artist_name}"
        params = {"q": query, "type": "track", "limit": 1}

        response = requests.get(search_url, headers=headers, params=params)
        result = response.json()

        if response.status_code == 200 and result.get("tracks", {}).get("items"):
            track = result["tracks"]["items"][0]
            track_uris.append(track["uri"])
        else:
            print(f"🔍 Not found on Spotify: {song_name} by {artist_name}")

    if not track_uris:
        return {"error": "❌ No matching Spotify tracks found."}

    # Step 3: Get user ID
    user_profile = requests.get("https://api.spotify.com/v1/me", headers=headers).json()
    user_id = user_profile.get("id")
    if not user_id:
        return {"error": "❌ Could not retrieve user profile."}

    # Step 4: Create new playlist
    playlist_data = {
        "name": "Groq Vibe Recommendations",
        "description": "Songs recommended by Groq based on your vibes 💫",
        "public": True
    }

    playlist_response = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json=playlist_data
    )

    if playlist_response.status_code != 201:
        return {"error": "❌ Failed to create playlist."}

    playlist_id = playlist_response.json()["id"]

    # Step 5: Add tracks
    add_response = add_tracks_to_playlist(playlist_id, track_uris, access_token)

    return {
        "message": "🎶 Groq songs added to playlist!",
        "playlist_id": playlist_id,
        "playlist_url": playlist_response.json()["external_urls"]["spotify"],
        "added_tracks": len(track_uris)
    }
    


# ──────────────────────────────────────────────
# 🔄 Refresh Spotify Access Token Route
# ──────────────────────────────────────────────
@app.post("/refresh_token")
def refresh_access_token():
    refresh_token = get_refresh_token()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        headers={
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if response.status_code != 200:
        return {"error": "❌ Failed to refresh token."}

    new_token_data = response.json()
    with open("token.json", "r") as f:
        current_token_data = json.load(f)

    # Update only access token
    current_token_data["access_token"] = new_token_data["access_token"]

    with open("token.json", "w") as f:
        json.dump(current_token_data, f, indent=4)

    return {"message": "✅ Access token refreshed."}


# ──────────────────────────────────────────────
# 🔎 Check Refresh Token Presence/Validity Route
# ──────────────────────────────────────────────
@app.get("/check_refresh_token")
def check_refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return {"valid": False}
    return {"valid": True}

from fastapi import Form

@app.post("/groq-recommend-vibe")
def recommend_vibe_based_music(vibe_prompt: str = Form(...)):
    access_token = get_access_token()
    
    # Step 1: Get top tracks
    top_tracks = get_user_top_tracks(access_token)
    liked_tracks_data = get_liked_songs(access_token)
    liked_tracks = extract_song_info_from_liked_tracks(liked_tracks_data)

    top_track_list = top_tracks.get("tracks", []) if isinstance(top_tracks, dict) else []
    combined_tracks = top_track_list + liked_tracks
    combined_tracks = combined_tracks[:20]  # Limit the list

    base_prompt = f"""
    You're a personalized music assistant.

    Here are 20 songs this user enjoys:
    {chr(10).join(combined_tracks)}

    The user has described their current mood or desired vibe as:
    "{vibe_prompt}"

    Based on these preferences, recommend 5 songs that match the same *emotional tone, musical style, and overall feel*.

    🎯 Guidelines:
    - prefer familiar songs.
    - Match the *language*, *genre*, and *energy level* if clear.
    - Output strictly in this format:
    1. **Song Name** by Artist
    2. ...
    """

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a smart, culturally aware music recommendation assistant who gives nuanced, context-specific suggestions."},
            {"role": "user", "content": base_prompt}
        ]
    )

    return {"groq_recommendations": response.choices[0].message.content}