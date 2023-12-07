from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.sql import select

from models.anti_choice_hist import anti_choice_history, AntiChoiceCreate
from database import database
from global_config import simulations_config

router = APIRouter(tags=["Anti Choice"])

# 선택은 한 번
@router.get("/anti_choice_check/{user_id}")
async def anti_choice_check(user_id: str):
    query = select(anti_choice_history.c.anti_choice).where(anti_choice_history.c.user_id == user_id)
    user_anti_choice = await database.fetch_one(query)
    if user_anti_choice is None:
        return {"user_anti_choice": None}  # Or any other appropriate response when no anti_choice has been made
    else:
        return {"user_anti_choice": user_anti_choice['anti_choice']}


@router.post("/anti_choose")
async def anti_choose_number(user_id: str = Query(example="test"), anti_choice: int = Query(example=0)):
    # Admin config로 통제 추가
    if simulations_config['anti_choice_enabled']:
        user_anti_choice = await anti_choice_check(user_id)

        # 아직 한 번도 등록하지 않았다면
        if user_anti_choice['user_anti_choice'] is None:
            anti_choice_data = AntiChoiceCreate(user_id=user_id, anti_choice=anti_choice)
            await database.execute(anti_choice_history.insert().values(**anti_choice_data.model_dump()))
        # 아니면 등록하면 안됨
        else:
            raise HTTPException(status_code=400, detail="한 번만 할 수 있어요!")

    else:
        return {"message": "아직 허가되지 않았습니다. 좀 이따 같이해요!"}