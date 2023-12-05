# main.py
from fastapi import FastAPI
from database import engine, metadata, database
from routers import auth, dice_simul, monty_hall, admin

from contextlib import asynccontextmanager

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

app.include_router(auth.router)
app.include_router(dice_simul.router)
app.include_router(monty_hall.router)
app.include_router(admin.router)