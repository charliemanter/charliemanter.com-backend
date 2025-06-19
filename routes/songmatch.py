import requests
from fastapi import APIRouter, Query
import os

router = APIRouter()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    return response.json().get("access_token")

@router.get("/songmatch")
def songmatch(title: str = Query(...), artist: str = Query(...)):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    search_url = "https://api.spotify.com/v1/search"
    params = {"q": f"track:{title} artist:{artist}", "type": "track", "limit": 1}
    track_resp = requests.get(search_url, headers=headers, params=params).json()
    items = track_resp.get("tracks", {}).get("items", [])
    if not items:
        return {"error": "Song not found"}
    track_id = items[0]["id"]

    rec_url = "https://api.spotify.com/v1/recommendations"
    rec_params = {"seed_tracks": track_id, "limit": 5}
    rec_resp = requests.get(rec_url, headers=headers, params=rec_params).json()
    recommendations = [
        {
            "title": t["name"],
            "artist": t["artists"][0]["name"],
            "preview_url": t["preview_url"],
            "album_art": t["album"]["images"][0]["url"],
            "spotify_url": t["external_urls"]["spotify"]
        }
        for t in rec_resp.get("tracks", [])
    ]
    return recommendations
