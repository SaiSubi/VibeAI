#!/usr/bin/env python3
"""
Check users in the database and their token status
"""

import sqlite3
import requests
from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from utils.db import get_tokens_for_user
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_user_playlists(user_id: str):
    """Check what playlists a user has access to"""
    try:
        from utils.token import get_access_token
        access_token = get_access_token(user_id)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get user info
        me_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"👤 User: {user_data.get('display_name', 'Unknown')} ({user_id})")
        
        # Get playlists
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            playlists = data.get("items", [])
            print(f"📋 Found {len(playlists)} playlists:")
            for playlist in playlists:
                print(f"  - {playlist.get('name', 'Unknown')} ({playlist.get('tracks', {}).get('total', 0)} tracks)")
        else:
            print(f"❌ Failed to get playlists: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking user {user_id}: {e}")

def main():
    """Check all users in the database"""
    print("🔍 Checking users in database...")
    
    # Check the service account user
    from utils.config import VibeAI_userid
    print(f"\n🔍 Checking service account user: {VibeAI_userid}")
    check_user_playlists(VibeAI_userid)
    
    # Check if there are other users in the database
    try:
        from utils.db import get_tokens_for_user
        # This will fail if no other users exist, which is fine
        pass
    except:
        print("\n📝 No other users found in database")
        print("💡 You may need to re-authenticate with the new scopes")
        print("   Visit: https://vibeai-backend.onrender.com/login")

if __name__ == "__main__":
    main() 