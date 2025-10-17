#!/usr/bin/env python3
"""
Minimal test version to isolate startup issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create minimal app
app = FastAPI(title="VibeAI Test")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Minimal test version"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Test basic imports without heavy initialization
@app.get("/test-imports")
async def test_imports():
    try:
        # Test if we can import v2 modules
        from routes.v2 import router
        return {"status": "success", "message": "v2 router imported successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
