# main.py
from fastapi import FastAPI
from database import engine, metadata, database
from routers import auth, dice_simul, monty_hall, admin, choice, anti_choice, stats, util

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# on_event가 deprecated라서 생김.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database를 처음에 연결할 것
    await database.connect()

    metadata.create_all(bind=engine)
    yield
    # 닫을 것
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(dice_simul.router)
app.include_router(monty_hall.router)
app.include_router(admin.router)
app.include_router(choice.router)
app.include_router(anti_choice.router)
app.include_router(stats.router)
app.include_router(util.router)