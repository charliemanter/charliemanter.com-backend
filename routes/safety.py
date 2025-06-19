# backend/routes/safety.py

from fastapi import APIRouter, HTTPException
import httpx, os, time

router = APIRouter(prefix="/safety", tags=["safety"])

@router.get("/lightning")
async def lightning_status():
    """
    Returns:
      {
        "last_strike":  timestamp (seconds since epoch) or null,
        "distance_miles": float or null,
        "safe": bool,
        "resume_at": ISO8601 or null
      }
    """
    key      = os.getenv("TOMORROW_API_KEY")
    lat      = os.getenv("LATITUDE")
    lon      = os.getenv("LONGITUDE")
    radius   = float(os.getenv("SAFE_RADIUS_MILES", 10))
    timeout  = int(os.getenv("SAFE_TIMEOUT_MIN", 30)) * 60

    params = {
      "apikey": key,
      "location": f"{lat},{lon}",
      "fields": ["lightningDistance","lightningStrikeCount"],
      "timesteps": ["1m"],
      "units": "imperial"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
          "https://api.tomorrow.io/v4/timelines", params=params, timeout=10
        )
    data = resp.json()
    if "errors" in data:
        raise HTTPException(502, detail=data["errors"])

    # grab the most recent minute of data
    point = data["data"]["timelines"][0]["intervals"][-1]["values"]
    dist  = point["lightningDistance"]
    count = point["lightningStrikeCount"]

    now = time.time()
    last_strike = now if (count and dist <= radius) else None

    # simple in-memory store of the last strike timestamp
    if not hasattr(lightning_status, "_last_strike"):
        lightning_status._last_strike = None
    if last_strike:
        lightning_status._last_strike = now

    lr   = lightning_status._last_strike
    safe = (lr is None) or (now - lr > timeout)
    resume_at = (
      time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(lr + timeout)))
      if lr else None
    )

    return {
      "last_strike":     lr,
      "distance_miles":  dist if count else None,
      "safe":            safe,
      "resume_at":       resume_at
    }
