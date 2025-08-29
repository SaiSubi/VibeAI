#!/usr/bin/env python3
"""
Test audio features access
"""

import requests
from utils.token import get_access_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_audio_features():
    """Test if we can access audio features"""
    try:
        access_token = get_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test with a known track ID (a popular song)
        test_track_id = "4iV5W9uYEdYUVa79Axb7Rh"  # "Shape of You" by Ed Sheeran
        
        print("🔍 Testing audio features access...")
        print(f"Track ID: {test_track_id}")
        
        url = f"https://api.spotify.com/v1/audio-features/{test_track_id}"
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            features = response.json()
            print("✅ Audio features access successful!")
            print(f"Valence: {features.get('valence')}")
            print(f"Energy: {features.get('energy')}")
            print(f"Danceability: {features.get('danceability')}")
            print(f"Tempo: {features.get('tempo')}")
        else:
            print(f"❌ Audio features access failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 403:
                print("\n💡 This is likely a scope issue.")
                print("You may need to re-authenticate with the new scopes.")
                print("Visit: https://vibeai-backend.onrender.com/login")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_audio_features() 