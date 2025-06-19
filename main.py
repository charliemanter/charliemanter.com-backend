from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.charliemanter.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze")
def analyze(username: str = Query(...), time_class: str = Query(...)):
    headers = {"User-Agent": "Chess Dashboard"}
    archive_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    try:
        archives = requests.get(archive_url, headers=headers).json()["archives"]
        all_games = []
        for url in archives:
            games = requests.get(url, headers=headers).json()["games"]
            filtered = [g for g in games if g.get("time_class") == time_class]
            all_games.extend(filtered)

        if not all_games:
            return {"error": "No games found."}

        wins, draws, losses, ratings = 0, 0, 0, []
        for g in all_games:
            color = 'white' if g['white']['username'].lower() == username.lower() else 'black'
            result = g[color]['result']
            rating = g[color].get('rating', 0)
            if result == "win": wins += 1
            elif result == "draw": draws += 1
            elif result: losses += 1
            if rating: ratings.append(rating)

        fig1, ax1 = plt.subplots()
        ax1.pie([wins, losses, draws], labels=['Wins', 'Losses', 'Draws'], autopct='%1.1f%%')
        ax1.set_title("Win Breakdown")
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        pie_data = base64.b64encode(buf1.read()).decode("utf-8")
        plt.close()

        fig2, ax2 = plt.subplots()
        ax2.plot(ratings, marker='o')
        ax2.set_title("Rating Progression")
        ax2.set_xlabel("Game #")
        ax2.set_ylabel("Rating")
        buf2 = io.BytesIO()
        plt.savefig(buf2, format="png")
        buf2.seek(0)
        line_data = base64.b64encode(buf2.read()).decode("utf-8")
        plt.close()

        return {
            "pie_chart": pie_data,
            "line_chart": line_data,
        }
    except Exception as e:
        return {"error": str(e)}
# Songmatch
from routes.songmatch import router as songmatch_router

app.include_router(songmatch_router)
