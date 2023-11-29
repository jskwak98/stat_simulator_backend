from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Table, Column, String
from database import metadata

# Pydantic model for request validation
class UserCreate(PydanticBaseModel):
    id: str  # Acts as the username
    password: str
    nickname: str

class UserInDB(PydanticBaseModel):
    id: str  # Acts as the username
    nickname: str

# SQLAlchemy model for the database
users = Table(
    "users",
    metadata,
    Column("id", String(50), primary_key=True),  # String-based ID as primary key
    Column("hashed_password", String),
    Column("nickname", String(50)),
)
