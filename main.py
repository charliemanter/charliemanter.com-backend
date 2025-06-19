# main.py
from dotenv import load_dotenv
load_dotenv()

import os, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from routes.songmatch import router as songmatch_router
from routes.chess_dash  import router as chess_dash_router
from routes.pool_safety   import router as pool_safety_router  # if you added lightning

app = FastAPI()

ALERT_ID = None

@app.on_event("startup")
async def register_lightning_alert():
    global ALERT_ID
    if ALERT_ID:
        return
    key    = os.getenv("TOMORROW_API_KEY")
    lat    = float(os.getenv("LATITUDE"))
    lon    = float(os.getenv("LONGITUDE"))
    buf    = [int(os.getenv("ALERT_BUFFER_MILES", 10))]
    ttl    = int(os.getenv("ALERT_TTL_MINUTES", 30))

    payload = {
      "location": {
        "type": "Point",
        "coordinates": [lon, lat]
      },
      "lightningConfig": {
        "buffers": buf,
        "distanceUnit": "mi",
        "ttl": ttl
      },
      "notifications": [
        { "type": "START" },
        { "type": "END",   "value": ttl }
      ]
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
          "https://api.tomorrow.io/v4/alerts",
          json=payload,
          headers={"apikey": key, "Content-Type":"application/json"}
        )
    data = resp.json()
    # Save alertId for later (e.g. in-memory or persistent store):
    ALERT_ID = data.get("data", {}).get("id")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.charliemanter.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount routers
app.include_router(songmatch_router)
app.include_router(chess_dash_router)
app.include_router(pool_safety_router)
