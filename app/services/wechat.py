"""WeChat Mini-Program API integration."""

from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()

CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def code2session(code: str) -> dict:
    """Exchange wx.login() code for openid + session_key."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            CODE2SESSION_URL,
            params={
                "appid": settings.wechat_appid,
                "secret": settings.wechat_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            },
        )
        data = resp.json()
    if "errcode" in data and data["errcode"] != 0:
        raise ValueError(f"WeChat API error: {data.get('errmsg', 'unknown')}")
    return data
