from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.songmatch import router as songmatch_router
from routes.chess_dash  import router as chess_dash_router
from routes.pool_safety   import router as pool_safety_router  # if you added lightning

app = FastAPI()

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
