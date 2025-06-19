# backend/routes/analyze.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import requests, matplotlib.pyplot as plt, io, base64

router = APIRouter(prefix="/analyze", tags=["chess"])

@router.get("/")
def analyze(username: str = Query(...), time_class: str = Query(...)):
    """
    Returns base64‐encoded pie and line charts for a Chess.com user.
    """
    headers = {"User-Agent": "Chess Dashboard"}
    try:
        # Fetch archives
        archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
        archives = requests.get(archives_url, headers=headers).json().get("archives", [])
        all_games = []
        for url in archives:
            games = requests.get(url, headers=headers).json().get("games", [])
            filtered = [g for g in games if g.get("time_class") == time_class]
            all_games.extend(filtered)

        if not all_games:
            raise HTTPException(404, f"No {time_class} games found for {username}.")

        ## compute stats
        wins = draws = losses = 0
        ratings = []
        for g in all_games:
            color = (
                "white"
                if g["white"]["username"].lower() == username.lower()
                else "black"
            )
            result = g[color]["result"]
            rating = g[color].get("rating")
            if result == "win":
                wins += 1
            elif result == "draw":
                draws += 1
            else:
                losses += 1
            if rating:
                ratings.append(rating)

        # Pie chart
        fig1, ax1 = plt.subplots()
        ax1.pie([wins, losses, draws], labels=["Wins", "Losses", "Draws"], autopct="%1.1f%%")
        ax1.set_title("Win Breakdown")
        buf1 = io.BytesIO(); plt.savefig(buf1, format="png"); buf1.seek(0); pie_data = base64.b64encode(buf1.read()).decode(); plt.close()

        # Line chart
        fig2, ax2 = plt.subplots()
        ax2.plot(ratings, marker="o")
        ax2.set_title("Rating Progression")
        ax2.set_xlabel("Game #"); ax2.set_ylabel("Rating")
        buf2 = io.BytesIO(); plt.savefig(buf2, format="png"); buf2.seek(0); line_data = base64.b64encode(buf2.read()).decode(); plt.close()

        return JSONResponse({"pie_chart": pie_data, "line_chart": line_data})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
