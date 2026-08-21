from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI-Powered Gamified DSA Learning Platform",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {
        "status": "ok",
        "judge0_configured": settings.judge0_configured,
        "gemini_configured": settings.gemini_configured,
    }
