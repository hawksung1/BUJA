from __future__ import annotations

import os
import httpx
from datetime import datetime, timedelta
from typing import Optional

NH_BASE_URL = os.getenv("NH_BASE_URL", "https://openapi.nhqv.com")
NH_APP_KEY = os.getenv("NH_APP_KEY", "")
NH_APP_SECRET = os.getenv("NH_APP_SECRET", "")
NH_ACCOUNT_NO = os.getenv("NH_ACCOUNT_NO", "")

_token_cache: dict = {"token": None, "expires_at": None}


def _get_token() -> Optional[str]:
    if not NH_APP_KEY or not NH_APP_SECRET:
        return None
    now = datetime.now()
    if _token_cache["token"] and _token_cache["expires_at"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]
    try:
        resp = httpx.post(
            f"{NH_BASE_URL}/oauth2/token",
            data={"grant_type": "client_credentials", "appkey": NH_APP_KEY, "appsecret": NH_APP_SECRET},
            timeout=10,
        )
        data = resp.json()
        token = data.get("access_token")
        if token:
            _token_cache["token"] = token
            _token_cache["expires_at"] = now + timedelta(hours=5, minutes=50)
        return token
    except Exception:
        return None


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}


def get_balance() -> dict:
    token = _get_token()
    if not token:
        return {"error": "NH OpenAPI 키가 설정되지 않았습니다. .env를 확인하세요."}
    try:
        resp = httpx.get(f"{NH_BASE_URL}/v1/account/balance", headers=_auth_headers(token), params={"account_no": NH_ACCOUNT_NO}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def get_holdings() -> list[dict]:
    token = _get_token()
    if not token:
        return []
    try:
        resp = httpx.get(f"{NH_BASE_URL}/v1/account/holdings", headers=_auth_headers(token), params={"account_no": NH_ACCOUNT_NO}, timeout=10)
        return resp.json().get("output", [])
    except Exception:
        return []


def get_order_history(start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
    token = _get_token()
    if not token:
        return []
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    try:
        resp = httpx.get(
            f"{NH_BASE_URL}/v1/account/orders",
            headers=_auth_headers(token),
            params={"account_no": NH_ACCOUNT_NO, "start_dt": start_date, "end_dt": end_date},
            timeout=10,
        )
        return resp.json().get("output", [])
    except Exception:
        return []


def is_configured() -> bool:
    return bool(NH_APP_KEY and NH_APP_SECRET and NH_ACCOUNT_NO)
