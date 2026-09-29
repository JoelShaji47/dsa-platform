from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.badges import router as badges_router
from app.api.v1.problems import (
    custom_router as custom_router,
    router as problems_router,
)
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.sql import router as sql_router
from app.api.v1.stats import router as stats_router
from app.api.v1.tests import router as tests_router
from app.api.v1.tutor import router as tutor_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.gamification import ensure_badge_catalog


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        ensure_badge_catalog(db)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI-Powered Gamified DSA Learning Platform",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(problems_router, prefix="/api/v1")
app.include_router(sql_router, prefix="/api/v1")
app.include_router(custom_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
app.include_router(badges_router, prefix="/api/v1")
app.include_router(tutor_router, prefix="/api/v1")
app.include_router(roadmap_router, prefix="/api/v1")
app.include_router(tests_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {
        "status": "ok",
        "judge0_configured": settings.judge0_configured,
        "gemini_configured": settings.gemini_configured,
    }
