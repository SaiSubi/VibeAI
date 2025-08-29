#!/usr/bin/env python3
"""
Refresh token and check playlists again
"""

import requests
from utils.token import get_access_token, refresh_access_token
from utils.config import VibeAI_userid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_and_check_playlists():
    """Refresh token and check all playlists"""
    try:
        # Force refresh the token
        print("🔄 Refreshing access token...")
        refresh_result = refresh_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        print(f"✅ Token refresh result: {refresh_result}")
        
        # Get fresh access token
        access_token = get_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        print("✅ Got fresh access token")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get user info
        me_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"👤 User: {user_data.get('display_name', 'Unknown')}")
        
        # Get all playlists with fresh token
        print("\n📋 Checking playlists with fresh token...")
        url = "https://api.spotify.com/v1/me/playlists"
        playlists = []
        offset = 0
        limit = 50
        
        while True:
            params = {"limit": limit, "offset": offset}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                batch_playlists = data.get("items", [])
                playlists.extend(batch_playlists)
                
                if len(batch_playlists) < limit:
                    break
                
                offset += limit
            else:
                print(f"❌ Failed to get playlists: {response.status_code}")
                print(f"Response: {response.text}")
                break
        
        print(f"\n📋 Found {len(playlists)} playlists:")
        print("=" * 60)
        
        for i, playlist in enumerate(playlists, 1):
            name = playlist.get("name", "Unknown")
            track_count = playlist.get("tracks", {}).get("total", 0)
            is_public = playlist.get("public", False)
            is_collaborative = playlist.get("collaborative", False)
            owner = playlist.get("owner", {}).get("display_name", "Unknown")
            
            print(f"{i:2d}. {name}")
            print(f"    Tracks: {track_count}")
            print(f"    Public: {is_public}")
            print(f"    Collaborative: {is_collaborative}")
            print(f"    Owner: {owner}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    refresh_and_check_playlists() 