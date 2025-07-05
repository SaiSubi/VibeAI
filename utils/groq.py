from typing import List, Tuple
import re
from utils.spotify import get_user_top_tracks, get_liked_songs, extract_song_info_from_liked_tracks
from openai import OpenAI
from utils.config import GROQ_API_KEY, logger

def get_user_music_history(access_token: str):
    # Step 1: Get top tracks
    top_tracks = get_user_top_tracks(access_token)
    if not top_tracks:
        logger.warning("❌ No top tracks found")
    liked_tracks_data = get_liked_songs(access_token)
    if not liked_tracks_data:
        logger.warning("❌ No liked tracks data found")
    liked_tracks = extract_song_info_from_liked_tracks(liked_tracks_data)

    top_track_list = top_tracks.get("tracks", []) if isinstance(top_tracks, dict) else []
    combined_tracks = top_track_list + liked_tracks
    combined_tracks = combined_tracks[:20]  # Limit the list
    return combined_tracks
def build_groq_prompt(combined_tracks, vibe_prompt):
    if not combined_tracks:
        return f"""
        You're a personalized music assistant.

        The user has described their current mood or desired vibe as:
        "{vibe_prompt}"

        Recommend 5 songs that match the emotional tone, musical style, and overall feel of this vibe.

        🎯 Guidelines:
        - prefer familiar songs.
        - Match the *language*, *genre*, and *energy level* if clear.
        - Output strictly in this format:
        1. **Song Name** by Artist
        2. ...
        """

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
    return base_prompt

def call_groq_api(prompt: str):
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a smart, culturally aware music recommendation assistant who gives nuanced, context-specific suggestions."},
            {"role": "user", "content": prompt}
        ]
    )

    return (response)

def extract_songs_from_groq_response(groq_response: str) -> List[Tuple[str, str]]:
    """
    Extracts (song, artist) pairs from Groq's response text.
    """
    lines = groq_response.split("\n")
    songs = []

    for line in lines:
        match = re.match(r"\d+\.\s+\*\*(.+?)\*\* by (.+?)\s*(?:-|$)", line.strip())
        if match:
            song_name, artist_name = match.groups()
            songs.append((song_name.strip(), artist_name.strip()))

    return songs
