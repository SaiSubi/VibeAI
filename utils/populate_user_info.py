#!/usr/bin/env python3
"""
Utility script to fetch user information from Spotify and fill missing name/email data
This script can be run independently to populate user info for existing users
"""

import sys
import os
import requests
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_users_without_info, update_user_info
from utils.token import refresh_access_token
from utils.config import logger

def get_user_info_from_spotify(user_id, access_token):
    """
    Fetch user information from Spotify API
    Returns (user_name, user_email) or (None, None) if failed
    """
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get("display_name")
            user_email = user_data.get("email")
            
            logger.info(f"✅ Fetched user info for {user_id}: {user_name}, {user_email}")
            return user_name, user_email
        else:
            logger.warning(f"❌ Failed to fetch user info for {user_id}: {response.status_code}")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ Error fetching user info for {user_id}: {e}")
        return None, None

def fill_missing_user_info():
    """
    Main function to fill missing user information
    """
    logger.info("🚀 Starting user info population process...")
    
    # Get users without complete info
    users_without_info = get_users_without_info()
    logger.info(f"📊 Found {len(users_without_info)} users with missing info")
    
    if not users_without_info:
        logger.info("✅ All users already have complete information!")
        return
    
    success_count = 0
    failed_count = 0
    
    for user_id, access_token in users_without_info:
        logger.info(f"🔍 Processing user: {user_id}")
        
        # Try to get user info from Spotify
        user_name, user_email = get_user_info_from_spotify(user_id, access_token)
        
        if user_name and user_email:
            # Update database with user info
            try:
                update_user_info(user_id, user_name, user_email)
                success_count += 1
                logger.info(f"✅ Updated user info for {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to update user info for {user_id}: {e}")
                failed_count += 1
        else:
            # Try refreshing the token and retry
            logger.info(f"🔄 Token might be expired for {user_id}, trying to refresh...")
            try:
                refresh_result = refresh_access_token(user_id)
                if refresh_result.get("success"):
                    # Get fresh access token and retry
                    from utils.db import get_tokens_for_user
                    tokens = get_tokens_for_user(user_id)
                    user_name, user_email = get_user_info_from_spotify(user_id, tokens["access_token"])
                    
                    if user_name and user_email:
                        update_user_info(user_id, user_name, user_email)
                        success_count += 1
                        logger.info(f"✅ Updated user info for {user_id} after token refresh")
                    else:
                        failed_count += 1
                        logger.warning(f"⚠️ Still couldn't fetch user info for {user_id} after token refresh")
                else:
                    failed_count += 1
                    logger.warning(f"⚠️ Couldn't refresh token for {user_id}")
            except Exception as e:
                logger.error(f"❌ Error refreshing token for {user_id}: {e}")
                failed_count += 1
    
    logger.info(f"🎉 User info population complete!")
    logger.info(f"✅ Successfully updated: {success_count} users")
    logger.info(f"❌ Failed to update: {failed_count} users")
    logger.info(f"📊 Total processed: {len(users_without_info)} users")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    
    fill_missing_user_info() 