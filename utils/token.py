import os
import base64
import requests
from datetime import datetime, timedelta
from utils.db import get_tokens_for_user, save_tokens_to_db
import logging
from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

logger = logging.getLogger(__name__)

def refresh_access_token(user_id: str):
    refresh_token = get_refresh_token(user_id)
    client_id = SPOTIFY_CLIENT_ID
    client_secret = SPOTIFY_CLIENT_SECRET

    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        headers={
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if response.status_code != 200:
        return {"error": "❌ Failed to refresh token."}

    new_token_data = response.json()
    new_access_token = new_token_data["access_token"]
    expires_in = new_token_data.get("expires_in", 3600)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Update token in DB
    save_tokens_to_db(
        user_id=user_id,
        access_token=new_access_token,
        refresh_token=refresh_token,
        expires_at=expires_at
    )

    return {"message": "✅ Access token refreshed."}

def get_access_token(user_id=None):

    if not user_id:
        raise Exception("❌ No user_id provided to get_access_token()")

    token_data = get_tokens_for_user(user_id)
    expires_at = token_data.get("expires_at")

    if not expires_at or (
        isinstance(expires_at, str) and datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%S.%f") < datetime.utcnow()
    ) or (
        isinstance(expires_at, datetime) and expires_at < datetime.utcnow()
    ):
        logger.info("🔄 Access token expired. Refreshing...")
        refresh_access_token(user_id)
        token_data = get_tokens_for_user(user_id)  # Fetch updated tokens

    return token_data["access_token"]

def get_refresh_token(user_id=None):
    if user_id:
        return get_tokens_for_user(user_id)["refresh_token"]
    else:
        raise Exception("❌ No user_id provided to get_refresh_token()")
    
