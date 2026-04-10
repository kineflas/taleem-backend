"""
Taliem FastAPI application entry point.

Startup:
  - APScheduler cron jobs (midnight MISSED marking + evening streak warning)
  - Surah + curriculum seed data (idempotent)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import SessionLocal
from .jobs.cron import create_scheduler
from .routers.auth import router as auth_router
from .routers.teacher import router as teacher_router
from .routers.tasks import router as tasks_router
from .routers.student import router as student_router
from .routers.notifications import router as notifications_router
from .routers.quran import router as quran_router
from .routers.curriculum import (
    content_router as curriculum_content_router,
    student_curriculum_router,
    teacher_curriculum_router,
)
from .seed.surahs import seed_surahs
from .seed.curriculum import seed_curriculum

settings = get_settings()
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    # 1. Seed static data (idempotent)
    try:
        db = SessionLocal()
        seed_surahs(db)
        seed_curriculum(db)
        db.close()
    except Exception as exc:
        logger.error("Seed failed: %s", exc)

    # 3. Cron scheduler
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("APScheduler started — midnight + evening jobs active")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped")


app = FastAPI(
    title="Taliem API",
    version="1.1.0",
    description="Backend for Taliem — Arabic & Quran learning companion",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [
        "https://taliem.app",
        "https://www.taliem.app",
        "https://taleem.cksyndic.ma",
        "https://www.taleem.cksyndic.ma",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(tasks_router)
app.include_router(student_router)
app.include_router(notifications_router)
app.include_router(quran_router)
app.include_router(curriculum_content_router)
app.include_router(student_curriculum_router)
app.include_router(teacher_curriculum_router)


# ── Static files ─────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.1.0"}
