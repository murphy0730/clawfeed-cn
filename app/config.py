"""Application configuration loaded from environment / .env file."""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> dict[str, str]:
    """Manually parse .env (same behaviour as the Node.js version)."""
    env_path = ROOT / ".env"
    result: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            eq = line.find("=")
            if eq > 0:
                result[line[:eq]] = line[eq + 1 :]
    return result


_dotenv = _load_dotenv()


def _get(key: str, default: str = "") -> str:
    return _dotenv.get(key) or os.environ.get(key, default)


class Settings(BaseSettings):
    # WeChat Mini-Program
    wechat_appid: str = _get("WECHAT_APPID")
    wechat_secret: str = _get("WECHAT_SECRET")

    # JWT
    jwt_secret: str = _get("JWT_SECRET", _get("SESSION_SECRET", "dev-jwt-secret"))
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 30

    # API key for internal / agent calls (POST /api/digests, PUT /api/config, …)
    api_key: str = _get("API_KEY")

    # CORS
    allowed_origins: list[str] = [
        o.strip()
        for o in _get("ALLOWED_ORIGINS", "localhost,127.0.0.1").split(",")
        if o.strip()
    ]

    # Database — SQLite by default, can switch to MySQL via DATABASE_URL
    # Uses a separate DB from the Node.js version to avoid schema conflicts
    database_url: str = _get(
        "DATABASE_URL",
        f"sqlite:///{ROOT / 'data' / 'clawfeed.db'}",
    )

    # Server
    port: int = int(_get("DIGEST_PORT", "8000"))
    host: str = _get("DIGEST_HOST", "127.0.0.1")
    base_url: str = _get("BASE_URL", "https://clawfeed.kevinhe.io")

    # Lark webhook for feedback notifications
    feedback_lark_webhook: str = _get("FEEDBACK_LARK_WEBHOOK")

    # LLM
    llm_api_key: str = _get("LLM_API_KEY")
    llm_base_url: str = _get("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = _get("LLM_MODEL", "gpt-4o-mini")

    # Scheduler
    scheduler_enabled: bool = _get("SCHEDULER_ENABLED", "false").lower() in ("true", "1", "yes")
    schedule_4h: str = _get("SCHEDULE_4H", "0 */4 * *")
    schedule_daily: str = _get("SCHEDULE_DAILY", "0 8 * *")
    schedule_weekly: str = _get("SCHEDULE_WEEKLY", "0 9 0 *")
    schedule_monthly: str = _get("SCHEDULE_MONTHLY", "0 9 * 1")

    model_config = {"env_prefix": "", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
