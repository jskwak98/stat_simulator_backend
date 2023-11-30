from pydantic import BaseModel
from sqlalchemy import Table, Column, String
from database import metadata

# Pydantic model for request validation
class UserCreate(BaseModel):
    user_id: str  # Acts as the username
    password: str
    nickname: str

class UserInDB(BaseModel):
    user_id: str  # Acts as the username
    nickname: str

# SQLAlchemy model for the database
users = Table(
    "users",
    metadata,
    Column("user_id", String(50), primary_key=True),  # String-based ID as primary key
    Column("hashed_password", String),
    Column("nickname", String(50)),
)
