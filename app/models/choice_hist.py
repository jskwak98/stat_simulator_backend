from pydantic import BaseModel, validator, Field
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from database import metadata

# Pydantic Model
class ChoiceCreate(BaseModel):
    user_id: str = Field(example="test")
    choice: int

    # 값을 체크하기
    @validator('choice')
    def validate_rolls(cls, v):
        if not 0 <= v <= 9:
            raise ValueError('0 이상 9 이하의 정수를 입력해주세요.')
        return v

# choice
choice_history = Table(
    "choice_history",
    metadata,
    Column("choice_id", Integer, primary_key=True, autoincrement=True),  # String-based ID as primary key
    Column("user_id", String, ForeignKey("users")),
    Column("choice", Integer),
)
