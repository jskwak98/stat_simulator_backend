from sqlalchemy import Table, Column, Integer, Boolean, String, ForeignKey
from database import metadata

from pydantic import BaseModel

class MontyHallResultCreate(BaseModel):
    user_id: str
    change: bool
    win: bool
    record: bool # 이걸 체크해서 실 기록용으로 쓰는지 확인하기

# 몬티 홀 내역 테이블
monty_hall_results = Table(
    "monty_hall_history",
    metadata,
    Column("monty_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, ForeignKey("users")),
    Column("change", Boolean),  # 첫 선택을 바꿨는지
    Column("win", Boolean)      # 승리하였는지
)