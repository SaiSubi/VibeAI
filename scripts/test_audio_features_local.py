#!/usr/bin/env python3
"""
Test audio features with tracks from your database
"""

import requests
import sqlite3
from utils.token import get_access_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_audio_features_local():
    """Test audio features with tracks from your database"""
    try:
        access_token = get_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get a track from your database
        conn = sqlite3.connect("song_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT spotify_id, title, artist FROM songs LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            spotify_id, title, artist = result
            print(f"🎵 Testing with: {title} by {artist}")
            print(f"🆔 Spotify ID: {spotify_id}")
            
            # Test audio features
            url = f"https://api.spotify.com/v1/audio-features/{spotify_id}"
            response = requests.get(url, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                features = response.json()
                print("✅ Audio features access successful!")
                print(f"Valence: {features.get('valence')}")
                print(f"Energy: {features.get('energy')}")
                print(f"Danceability: {features.get('danceability')}")
                print(f"Tempo: {features.get('tempo')}")
                return True
            else:
                print(f"❌ Audio features access failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print("❌ No tracks found in database")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_audio_features_local() 