from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.badges import router as badges_router
from app.api.v1.problems import (
    custom_router as custom_router,
    router as problems_router,
)
from app.api.v1.leagues import router as leagues_router
from app.api.v1.profile import router as profile_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.shop import router as shop_router
from app.api.v1.sql import router as sql_router
from app.api.v1.stats import router as stats_router
from app.api.v1.tests import router as tests_router
from app.api.v1.custom_roadmaps import router as custom_roadmaps_router
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
app.include_router(admin_router, prefix="/api/v1")
app.include_router(problems_router, prefix="/api/v1")
app.include_router(sql_router, prefix="/api/v1")
app.include_router(custom_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
app.include_router(badges_router, prefix="/api/v1")
app.include_router(tutor_router, prefix="/api/v1")
app.include_router(roadmap_router, prefix="/api/v1")
app.include_router(leagues_router, prefix="/api/v1")
app.include_router(shop_router, prefix="/api/v1")
app.include_router(tests_router, prefix="/api/v1")
app.include_router(custom_roadmaps_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {
        "status": "ok",
        "judge0_configured": settings.judge0_configured,
        "gemini_configured": settings.gemini_configured,
    }


@app.get("/health/ml", tags=["system"])
def ml_health_check() -> dict:
    """Public deployment check for the recommender artifacts."""
    from app.ml import infer, retrieval

    ranker = infer.model_version()
    return {
        "status": "ok" if ranker else "heuristic",
        "ranker": ranker,
        "ranker_loaded": infer.artifact_loaded(),
        "ranker_compatible": infer.artifact_compatible(),
        "retrieval": retrieval.model_version(),
    }


_ML_TEST_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recommender model check</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin: 0; min-height: 100vh; display: grid; place-items: center;
    background: #0b0c0f; color: #f4f1ea; font-family: ui-sans-serif, system-ui,
    -apple-system, "Segoe UI", sans-serif; }
  main { width: min(560px, calc(100% - 32px)); padding: 28px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,.12); background: #13151a;
    box-shadow: 0 20px 60px rgba(0,0,0,.4); }
  h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: -.03em; }
  p { margin: 0; color: #9ea7b3; line-height: 1.5; }
  button { width: 100%; margin-top: 20px; padding: 14px 18px; border: 0;
    border-radius: 12px; background: #f4f1ea; color: #111318; font: inherit;
    font-weight: 700; cursor: pointer; }
  button:disabled { opacity: .6; cursor: wait; }
  pre { margin: 18px 0 0; padding: 16px; border-radius: 12px;
    background: #0b0c0f; border: 1px solid rgba(255,255,255,.08);
    color: #c9d1d9; font-size: 13px; line-height: 1.5; white-space: pre-wrap;
    word-break: break-word; }
  .hint { margin-top: 10px; font-size: 12px; color: #737d8c; }
</style>
</head>
<body>
<main>
  <p class="hint">DSA Platform &middot; deployment check</p>
  <h1>Recommender model</h1>
  <p>Click the button to ask the API which model is loaded.</p>
  <button id="run" type="button">Test model</button>
  <pre id="out">Waiting for test&hellip;</pre>
  <p class="hint">Public health check. It never exposes user data.</p>
</main>
<script>
  const out = document.getElementById("out");
  const btn = document.getElementById("run");
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    out.textContent = "Testing...";
    try {
      const res = await fetch("/health/ml", { cache: "no-store" });
      const data = await res.json();
      out.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      out.textContent = "Request failed: " + err;
    } finally {
      btn.disabled = false;
    }
  });
</script>
</body>
</html>
"""


@app.get("/ml-test", response_class=HTMLResponse, include_in_schema=False)
def ml_test_page() -> str:
    return _ML_TEST_PAGE
