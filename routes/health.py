from fastapi import APIRouter

router = APIRouter()

# ──────────────────────────────────────────────
# 🌐 Basic Health Check Route
# ──────────────────────────────────────────────
@router.get("/")
def root():
    return {"message": "VibeAI backend is live!"}

# Health check endpoint
@router.get("/health")
def health_check():
    return {"status": "ok"}