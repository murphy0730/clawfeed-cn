"""FastAPI application entry-point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, ROOT
from app.database import engine, Base
from app.routers import auth, digests, marks, sources, subscriptions, packs, feedback, feed, config
from app.scheduler import start_scheduler, stop_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (like the Node.js migration-on-boot pattern)
    Path(ROOT / "data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="ClawFeed API",
    description="AI-powered news digest — WeChat Mini-Program + Web backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all in dev, configured origins in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(digests.router)
app.include_router(marks.router)
app.include_router(sources.router)
app.include_router(subscriptions.router)
app.include_router(packs.router)
app.include_router(feedback.router)
app.include_router(feed.router)
app.include_router(config.router)


@app.get("/api/health")
@app.get("/health")
async def health():
    return {"status": "ok"}
