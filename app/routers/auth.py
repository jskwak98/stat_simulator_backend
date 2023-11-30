from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.sql import select
from passlib.context import CryptContext
from models.user import users, UserCreate, UserInDB
from database import database
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(user_id=user.user_id, hashed_password=hashed_password, nickname=user.nickname)
    last_record_id = await database.execute(query)
    return {"id": last_record_id, "nickname": user.nickname}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(username: str):
    query = select([users]).where(users.c.user_id == username)
    return await database.fetch_one(query)

@router.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    user = await get_user(credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"message": "Login successful for user: {}".format(user.user_id)}
