#!/usr/bin/env python3
"""
Check playlists using different API endpoints
"""

import requests
from utils.token import get_access_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_all_playlist_endpoints():
    """Check playlists using different API endpoints"""
    try:
        access_token = get_access_token("31r4bejefnssdwtcfgw6kf3niv4i")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get user ID
        me_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            user_id = user_data["id"]
            print(f"👤 User: {user_data.get('display_name', 'Unknown')} (ID: {user_id})")
        
        # Method 1: /me/playlists (current method)
        print("\n📋 Method 1: /me/playlists")
        url1 = "https://api.spotify.com/v1/me/playlists"
        response1 = requests.get(url1, headers=headers)
        if response1.status_code == 200:
            data1 = response1.json()
            playlists1 = data1.get("items", [])
            print(f"Found {len(playlists1)} playlists:")
            for playlist in playlists1:
                print(f"  - {playlist.get('name', 'Unknown')} ({playlist.get('tracks', {}).get('total', 0)} tracks)")
        
        # Method 2: /users/{user_id}/playlists
        print(f"\n📋 Method 2: /users/{user_id}/playlists")
        url2 = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        response2 = requests.get(url2, headers=headers)
        if response2.status_code == 200:
            data2 = response2.json()
            playlists2 = data2.get("items", [])
            print(f"Found {len(playlists2)} playlists:")
            for playlist in playlists2:
                print(f"  - {playlist.get('name', 'Unknown')} ({playlist.get('tracks', {}).get('total', 0)} tracks)")
        
        # Method 3: Check if there are more playlists with pagination
        print(f"\n📋 Method 3: Check for more playlists with pagination")
        url3 = "https://api.spotify.com/v1/me/playlists?limit=100"
        response3 = requests.get(url3, headers=headers)
        if response3.status_code == 200:
            data3 = response3.json()
            playlists3 = data3.get("items", [])
            print(f"Found {len(playlists3)} playlists with limit=100:")
            for playlist in playlists3:
                name = playlist.get('name', 'Unknown')
                tracks = playlist.get('tracks', {}).get('total', 0)
                public = playlist.get('public', False)
                print(f"  - {name} ({tracks} tracks, Public: {public})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_all_playlist_endpoints() 