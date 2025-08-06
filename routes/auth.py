from fastapi import APIRouter, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse
import urllib.parse
import base64
from datetime import datetime, timedelta
import requests
from typing import Optional
from utils.config import (
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI, FRONTEND_URL
)
from utils.db import save_tokens_to_db, get_tokens_for_user, logout_user_from_db, check_user_registered
import logging
from utils.token import refresh_access_token

router = APIRouter()
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 🎧 Spotify Login Route
# ──────────────────────────────────────────────
@router.get("/login")
def login():
    logger.info(f"🧭 REDIRECT_URI during login: {SPOTIFY_REDIRECT_URI}")
    scopes = "user-library-read playlist-modify-public user-top-read user-read-email"
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
    # Get user's Spotify ID and info
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if user_response.status_code != 200:
        return {"error": "❌ Failed to retrieve user info from Spotify."}

    user_data = user_response.json()
    user_id = user_data["id"]
    user_name = user_data.get("display_name")
    user_email = user_data.get("email")

    # Debug logging
    logger.info(f"🔍 Spotify user data received: {user_data}")
    logger.info(f"🔍 User ID: {user_id}")
    logger.info(f"🔍 User name: {user_name}")
    logger.info(f"🔍 User email: {user_email}")
    logger.info(f"🔍 Available fields in user_data: {list(user_data.keys())}")

    # Calculate token expiry
    expires_in = token_data.get("expires_in", 3600)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Save to DB with user info
    try:
        save_tokens_to_db(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at,
            user_name=user_name,
            user_email=user_email
        )
        logger.info(f"✅ Successfully saved user info to database for {user_id}")
    except Exception as e:
        logger.error(f"❌ Error saving user info to database: {e}")
        # Still save tokens even if user info fails
        save_tokens_to_db(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at
        )

    logger.info(f"✅ Redirecting user_id to frontend.")
    redirect = RedirectResponse(url=f"{FRONTEND_URL}/home?user_id={user_id}")
    return redirect

@router.get("/check_refresh_token")
def check_refresh_token(user_id: Optional[str] = None):
    if not user_id:
        logger.warning("❌ No user_id provided.")
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

@router.get("/check_user_registered")
def check_user_registered_endpoint(user_id: Optional[str] = None):
    if not user_id:
        logger.warning("❌ No user_id provided.")
        return {"registered": False}

    try:
        is_registered = check_user_registered(user_id)
        logger.info(f"✅ User {user_id} registration check: {is_registered}")
        return {"registered": is_registered}
    except Exception as e:
        logger.error(f"❌ Error checking user registration: {e}")
        return {"registered": False}

@router.post("/refresh_token")
def refresh_token_endpoint(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    if not user_id:
        return JSONResponse(content={"error": "❌ No user_id provided"}, status_code=400)

    result = refresh_access_token(user_id)
    return JSONResponse(content=result)

# ──────────────────────────────────────────────
# 🚪 Logout Route: Remove User Tokens
# ──────────────────────────────────────────────
@router.post("/logout")
def logout_user(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    if not user_id:
        return JSONResponse(content={"error": "❌ No user_id provided"}, status_code=400)

    try:
        success = logout_user_from_db(user_id)
        if success:
            logger.info(f"✅ Successfully logged out user: {user_id}")
            return JSONResponse(content={
                "message": "✅ Successfully logged out",
                "success": True
            })
        else:
            logger.warning(f"⚠️ User not found for logout: {user_id}")
            return JSONResponse(content={
                "message": "⚠️ User not found",
                "success": False
            })
    except Exception as e:
        logger.error(f"❌ Error during logout: {e}")
        return JSONResponse(content={
            "error": "❌ Error during logout",
            "success": False
        }, status_code=500)