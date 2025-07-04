# Sets up the backend application with CORS settings (Cross-Origin Resource Sharing)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.config import ALLOWED_ORIGINS

def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,  # List of allowed origins from the config
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app