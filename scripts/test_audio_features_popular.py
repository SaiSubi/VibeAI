#!/usr/bin/env python3
"""
Test audio features with a very popular track
"""

import requests
from utils.token import get_access_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_audio_features_popular():
    """Test audio features with a very popular track"""
    try:
        access_token = get_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try with "Blinding Lights" by The Weeknd (one of the most streamed songs)
        test_track_id = "0VjIjW4GlUZAMYd2vXMi3b"
        
        print("🔍 Testing audio features with 'Blinding Lights' by The Weeknd...")
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
            return True
        else:
            print(f"❌ Audio features access failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Let's also try the client credentials flow
            print("\n🔄 Trying client credentials flow...")
            from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
            import base64
            
            auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
            b64_auth_str = base64.b64encode(auth_str.encode()).decode()
            
            token_response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                headers={"Authorization": f"Basic {b64_auth_str}"}
            )
            
            if token_response.status_code == 200:
                client_token = token_response.json()["access_token"]
                client_headers = {"Authorization": f"Bearer {client_token}"}
                
                client_response = requests.get(url, headers=client_headers)
                if client_response.status_code == 200:
                    features = client_response.json()
                    print("✅ Audio features accessible with client credentials!")
                    print(f"Valence: {features.get('valence')}")
                    print(f"Energy: {features.get('energy')}")
                    return True
                else:
                    print(f"❌ Client credentials also failed: {client_response.status_code}")
            else:
                print(f"❌ Client credentials token failed: {token_response.status_code}")
            
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_audio_features_popular() 