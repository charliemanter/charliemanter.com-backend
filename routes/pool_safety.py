from fastapi import APIRouter, Request, HTTPException
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/safety", tags=["safety"])

# In-memory safety state
_status = {"safe": True, "resume_at": None}

@router.post("/webhook")
async def lightning_webhook(req: Request):
    """
    Webhook endpoint for Tomorrow.io Alerts API.
    Expects payload with 'alertId', 'type' ('START' or 'END'), and 'timestamp'.
    """
    payload = await req.json()
    alert_type = payload.get("type")
    ts = payload.get("timestamp")

    if alert_type == "START":
        # Lightning detected: swimming OFF
        _status["safe"] = False
        ttl = int(os.getenv("ALERT_TTL_MINUTES", 30))
        # Calculate all-clear time
        resume_time = datetime.fromisoformat(ts.replace("Z", "+00:00")) + timedelta(minutes=ttl)
        _status["resume_at"] = resume_time.isoformat()
    elif alert_type == "END":
        # All-clear notification: swimming ON
        _status["safe"] = True
        _status["resume_at"] = None
    else:
        raise HTTPException(400, f"Unknown notification type: {alert_type}")

    return {"ok": True}

@router.get("/lightning-status")
async def get_lightning_status():
    """
    Returns:
      { "safe": bool, "resume_at": ISO8601 string or None }
    """
    return _status
