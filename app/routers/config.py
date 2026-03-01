"""Config + Changelog + Roadmap routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import ROOT
from app.deps import get_db, verify_api_key
from app import crud

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/changelog")
async def get_changelog(lang: str = "en"):
    suffix = ".zh.md" if lang == "zh" else ".md"
    path = ROOT / f"CHANGELOG{suffix}"
    try:
        return {"content": path.read_text(encoding="utf-8")}
    except FileNotFoundError:
        return {"content": "# Changelog\n\nNo changelog found."}


@router.get("/roadmap")
async def get_roadmap(lang: str = "en"):
    suffix_map = {"zh": ".zh.md", "en": ".en.md"}
    suffix = suffix_map.get(lang, ".md")
    path = ROOT / f"ROADMAP{suffix}"
    try:
        return {"content": path.read_text(encoding="utf-8")}
    except FileNotFoundError:
        return {"content": "# Roadmap\n\nNo roadmap found."}


@router.get("/config")
async def get_config(db: Session = Depends(get_db)):
    return crud.get_config(db)


@router.put("/config")
async def update_config(
    data: dict,
    _api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    for k, v in data.items():
        crud.set_config(db, k, v)
    return {"ok": True}
