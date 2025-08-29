#!/usr/bin/env python3
"""
Test if Spotify credentials are working
"""

import requests
from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_spotify_credentials():
    """Test if Spotify credentials are working"""
    try:
        print("🔍 Testing Spotify credentials...")
        
        # Test client credentials flow
        auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        
        print(f"Client ID: {SPOTIFY_CLIENT_ID[:10]}...")
        print(f"Client Secret: {SPOTIFY_CLIENT_SECRET[:10]}...")
        
        token_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {b64_auth_str}"}
        )
        
        print(f"Token response status: {token_response.status_code}")
        
        if token_response.status_code == 200:
            client_token = token_response.json()["access_token"]
            print("✅ Client credentials token obtained")
            
            # Test a simple endpoint
            headers = {"Authorization": f"Bearer {client_token}"}
            
            # Test search endpoint
            search_response = requests.get(
                "https://api.spotify.com/v1/search?q=test&type=track&limit=1",
                headers=headers
            )
            
            print(f"Search response status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                print("✅ Search endpoint working")
                
                # Try audio features again with client token
                test_track_id = "0VjIjW4GlUZAMYd2vXMi3b"  # Blinding Lights
                audio_response = requests.get(
                    f"https://api.spotify.com/v1/audio-features/{test_track_id}",
                    headers=headers
                )
                
                print(f"Audio features response status: {audio_response.status_code}")
                
                if audio_response.status_code == 200:
                    features = audio_response.json()
                    print("✅ Audio features working with client credentials!")
                    print(f"Valence: {features.get('valence')}")
                    print(f"Energy: {features.get('energy')}")
                else:
                    print(f"❌ Audio features failed: {audio_response.status_code}")
                    print(f"Response: {audio_response.text}")
            else:
                print(f"❌ Search failed: {search_response.status_code}")
        else:
            print(f"❌ Client credentials failed: {token_response.status_code}")
            print(f"Response: {token_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_spotify_credentials() 