#!/usr/bin/env python3
"""
Check the current token's scopes
"""

import requests
from utils.token import get_access_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_token_scopes():
    """Check what scopes the current token has"""
    try:
        access_token = get_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get user info to see what we can access
        me_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"✅ User info accessible: {user_data.get('display_name')}")
        
        # Try to get user's playlists
        playlists_response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
        if playlists_response.status_code == 200:
            print("✅ Playlists accessible")
        else:
            print(f"❌ Playlists not accessible: {playlists_response.status_code}")
        
        # Try to get user's top tracks
        top_tracks_response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)
        if top_tracks_response.status_code == 200:
            print("✅ Top tracks accessible")
        else:
            print(f"❌ Top tracks not accessible: {top_tracks_response.status_code}")
        
        # Try to get user's liked songs
        liked_songs_response = requests.get("https://api.spotify.com/v1/me/tracks", headers=headers)
        if liked_songs_response.status_code == 200:
            print("✅ Liked songs accessible")
        else:
            print(f"❌ Liked songs not accessible: {liked_songs_response.status_code}")
        
        # Try audio features again
        test_track_id = "4iV5W9uYEdYUVa79Axb7Rh"
        audio_features_response = requests.get(f"https://api.spotify.com/v1/audio-features/{test_track_id}", headers=headers)
        if audio_features_response.status_code == 200:
            print("✅ Audio features accessible")
            features = audio_features_response.json()
            print(f"   Valence: {features.get('valence')}")
            print(f"   Energy: {features.get('energy')}")
        else:
            print(f"❌ Audio features not accessible: {audio_features_response.status_code}")
            print(f"   Response: {audio_features_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_token_scopes() 