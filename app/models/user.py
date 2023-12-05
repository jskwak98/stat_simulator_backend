from pydantic import BaseModel, Field
from sqlalchemy import Table, Column, String
from database import metadata

# Pydantic model for request validation
class UserCreate(BaseModel):
    user_id: str = Field(example="test") # Acts as the username
    password: str = Field(example="test")
    nickname: str = Field(example="test")

# SQLAlchemy model for the database
users = Table(
    "users",
    metadata,
    Column("user_id", String(50), primary_key=True),  # String-based ID as primary key
    Column("hashed_password", String),
    Column("nickname", String(50)),
)
