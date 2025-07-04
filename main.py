# main.py

# ──────────────────────────────────────────────
# 🧱 Imports and Setup
# ──────────────────────────────────────────────
# main.py

# ──────────────────────────────────────────────
# 🧱 Imports and Setup
# ──────────────────────────────────────────────
import os
import urllib.parse
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
# Load environment variables from config file
# Load environment variables from config file
from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, GROQ_API_KEY, DATABASE_URL, FRONTEND_URL
# Set up logging
import logging
logger = logging.getLogger(__name__)
# Import the app factory
from utils.app_factory import create_app

from utils.db import save_tokens_to_db, get_tokens_for_user

from utils.spotify import create_playlist, add_tracks_to_playlist

# Token utilities
from utils.token import get_access_token, get_refresh_token, refresh_access_token

from routes import playlist, reco, extra, auth, health
# 🚀 FastAPI App Init
app = create_app()

app.include_router(auth.router)
app.include_router(playlist.router)
app.include_router(reco.router)
app.include_router(extra.router)
app.include_router(health.router)
