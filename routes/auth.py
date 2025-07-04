from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import urllib.parse
import base64
from datetime import datetime, timedelta
import requests
from utils.config import (
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI, FRONTEND_URL
)
from utils.db import save_tokens_to_db, get_tokens_for_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 🎧 Spotify Login Route
# ──────────────────────────────────────────────
@router.get("/login")
def login():
    logger.info(f"🧭 REDIRECT_URI during login: {SPOTIFY_REDIRECT_URI}")
    scopes = "user-library-read playlist-modify-public user-top-read"
    auth_url = "https://accounts.spotify.com/authorize"

    query_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scopes,
    }

    # Redirect user to Spotify's login screen
    url = f"{auth_url}?{urllib.parse.urlencode(query_params)}"
    return RedirectResponse(url)

# ──────────────────────────────────────────────
# 🔁 Spotify Callback: Get Access + Refresh Token
# ──────────────────────────────────────────────
@router.get("/callback")
def callback(request: Request, code: str):
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI
        },
        headers={
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if response.status_code != 200:
        return {"error": response.json()}

    token_data = response.json()
    # Get user's Spotify ID
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if user_response.status_code != 200:
        return {"error": "❌ Failed to retrieve user info from Spotify."}

    user_id = user_response.json()["id"]

    # Calculate token expiry
    expires_in = token_data.get("expires_in", 3600)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Save to DB
    save_tokens_to_db(
        user_id=user_id,
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        expires_at=expires_at
    )

    # Set refresh token and user_id in cookies with correct options for secure cross-origin/frontend access
    logger.info(f"➡️ FRONTEND_URL: {FRONTEND_URL}")
    redirect = RedirectResponse(url=f"{FRONTEND_URL}/home")
    redirect.set_cookie(
        key="refresh_token",
        value=token_data["refresh_token"],
        httponly=True,
        samesite="none",
        secure=True
    )
    redirect.set_cookie(
        key="user_id",
        value=user_id,
        httponly=False,
        samesite="none",
        secure=True
    )

    return redirect

@router.get("/check_refresh_token")
def check_refresh_token(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        logger.warning("❌ No user_id cookie found.")
        return {"valid": False}

    try:
        tokens = get_tokens_for_user(user_id)
        if not tokens or "refresh_token" not in tokens:
            logger.warning(f"❌ No token found in DB for user: {user_id}")
            return {"valid": False}
        return {"valid": True}
    except Exception as e:
        logger.error(f"❌ Error checking refresh token: {e}")
        return {"valid": False}