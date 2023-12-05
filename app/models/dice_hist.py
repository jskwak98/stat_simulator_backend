from pydantic import BaseModel, validator, Field
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from database import metadata

# Pydantic Model
class DiceRollCreate(BaseModel):
    user_id: str = Field(example="test")
    rolls: list[int]

    # 값을 체크하기
    @validator('rolls')
    def validate_rolls(cls, v):
        if len(v) != 6 or not all(1 <= roll <= 100 for roll in v):
            raise ValueError('6개의 1~100 사이의 주사위를 굴려야 합니다.')
        return v
    
    # db에 들어가기 위한 json으로 convert하기
    def to_db_model(self):
        return {
            "user_id" : self.user_id,
            "rolls" : ",".join(map(str, self.rolls)),
            "sum_of_rolls" : sum(self.rolls)
        }

# Roll History of Dice, SQLITE에 들어감
dice_history = Table(
    "dice_history",
    metadata,
    Column("roll_id", Integer, primary_key=True, autoincrement=True),  # String-based ID as primary key
    Column("user_id", String, ForeignKey("users")),
    Column("rolls", String),
    Column("sum_of_rolls", Integer),
)
