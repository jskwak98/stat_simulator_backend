from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.sql import select

from models.choice_hist import choice_history, ChoiceCreate
from database import database
from global_config import simulations_config

router = APIRouter(tags=["Choice"])

# 선택은 한 번
@router.get("/choice_check/{user_id}")
async def choice_check(user_id: str):
    query = select(choice_history.c.choice).where(choice_history.c.user_id == user_id)
    user_choice = await database.fetch_one(query)
    if user_choice is None:
        return {"user_choice": None}  # Or any other appropriate response when no choice has been made
    else:
        return {"user_choice": user_choice['choice']}


@router.post("/choose")
async def choose_number(user_id: str = Query(example="test"), choice: int = Query(example=0)):
    # Admin config로 통제 추가
    if simulations_config['choice_enabled']:
        user_choice = await choice_check(user_id)

        # 아직 한 번도 등록하지 않았다면
        if user_choice['user_choice'] is None:
            choice_data = ChoiceCreate(user_id=user_id, choice=choice)
            await database.execute(choice_history.insert().values(**choice_data.model_dump()))
            return {"message": f"{choice}를 선택했어요!"}
        # 아니면 등록하면 안됨
        else:
            return {"message": "한 번만 할 수 있어요!"}
    else:
        return {"message": "아직 허가되지 않았습니다. 좀 이따 같이해요!"}