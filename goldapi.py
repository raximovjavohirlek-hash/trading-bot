import os
import time

import httpx

GOLDAPI_KEY = os.getenv("GOLDAPI_KEY")
GOLDAPI_URL = "https://www.goldapi.io/api/XAU/USD"

_CACHE_TTL_SECONDS = 30
_cache = {"data": None, "fetched_at": 0.0}


class GoldDataUnavailable(Exception):
    pass


async def get_xauusd_price() -> dict:
    """Returns latest XAUUSD snapshot. Raises GoldDataUnavailable if the
    upstream API fails or the key is missing — callers must not fabricate
    a price when this happens."""
    if not GOLDAPI_KEY:
        raise GoldDataUnavailable("GOLDAPI_KEY topilmadi (.env tekshiring)")

    now = time.time()
    if _cache["data"] and (now - _cache["fetched_at"]) < _CACHE_TTL_SECONDS:
        return _cache["data"]

    headers = {"x-access-token": GOLDAPI_KEY, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(GOLDAPI_URL, headers=headers)
        resp.raise_for_status()
        payload = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GoldDataUnavailable(f"GoldAPI so'rovi muvaffaqiyatsiz: {exc}") from exc

    if "price" not in payload:
        raise GoldDataUnavailable(f"GoldAPI kutilmagan javob qaytardi: {payload}")

    _cache["data"] = payload
    _cache["fetched_at"] = now
    return payload
