from fastapi import APIRouter, HTTPException
from sqlalchemy.sql import func

from models.dice_hist import dice_history, DiceRollCreate
from database import database

from random import randint

MAX_ROLLS = 20

router = APIRouter()

# 유효한 Valid Roll 개수를 check함
@router.get("/roll_check/{user_id}")
async def roll_check(user_id: str):
    query = func.count().select().where(dice_history.c.user_id == user_id)
    total_rolls = await database.fetch_val(query)
    return {"total_rolls": total_rolls}


@router.post("/roll")
async def roll_dice(user_id: str, record: bool):
    # 등록하고 싶어한다면
    if record:
        # 먼저 DB에 등록 가능한 상태인지 check한다.
        total_rolls = await roll_check(user_id)

        # 본인이 원하고, 등록 가능하다면 등록한다.
        if total_rolls['total_rolls'] < MAX_ROLLS:
            # 실제로 굴린다
            rolls = [randint(1, 100) for _ in range(6)]
            roll_data = DiceRollCreate(user_id=user_id, rolls=rolls)
            await database.execute(dice_history.insert().values(**roll_data.to_db_model()))
        # 아니면 등록하면 안됨
        else:
            raise HTTPException(status_code=400, detail="20번 다 굴렸어요!")

    # 비 기록용 굴리기
    else:
        rolls = [randint(1, 100) for _ in range(6)]

    # 굴린 결과는 결과대로 return
    return {"rolls": rolls, "sum_of_rolls": sum(rolls)}
