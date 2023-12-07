# Frontend 에서 실행하고 back으로 결과를 넘기기로 했다
# js 잘 짜보자

from fastapi import APIRouter
from models.monty_hist import monty_hall_history, MontyHallResultCreate
from database import database
from sqlalchemy.sql import func
from global_config import simulations_config

router = APIRouter(tags=["Monty Hall"])

MAX_MONTY_HALL_TRIALS = 7

# 몬티 홀 총 시행횟수 체크하는 api
@router.get("/monty_hall_trials/{user_id}")
async def get_monty_hall_trial_count(user_id: str):
    # user_id로 monty_hall history 찾고 반환
    # Frontend에서도 사용할 것
    query = func.count().select().where(monty_hall_history.c.user_id == user_id)
    total_trials = await database.fetch_val(query)
    return {"total_trials": total_trials}


# 몬티 홀 시행 후 db 저장
@router.post("/monty_hall")
async def record_monty_hall_result(result: MontyHallResultCreate):
    # Admin config로 통제 추가
    if simulations_config['monty_hall_enabled']:
        # 기록하고자 한다면
        if result.record:
            # 기록 확인해주고
            trial_count_response = await get_monty_hall_trial_count(result.user_id)
            total_trials = trial_count_response["total_trials"]

            # MAX보다 적다면 기록해준다.
            if total_trials < MAX_MONTY_HALL_TRIALS:
                insert_query = monty_hall_history.insert().values(user_id=result.user_id, change=result.change, win=result.win)
                await database.execute(insert_query)
                return {"message": "기록되었습니다!"}
            
            # 도전 기회를 모두 소모함
            else:
                return {"message": "도전 기회를 모두 소모하였기에 기록에 남지 않습니다."}
        # 비 기록용임
        return {"message": "별도로 기록되지 않습니다."}
    else:
        return {"message": "아직 허가되지 않았습니다. 좀 이따 같이해요!"}