# main.py
from fastapi import FastAPI
from database import engine, metadata, database
from routers import auth

from contextlib import asynccontextmanager

# on_event가 deprecated라서 생김.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database를 처음에 연결할 것
    await database.connect()
    yield
    # 닫을 것
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

metadata.create_all(bind=engine)

app.include_router(auth.router)