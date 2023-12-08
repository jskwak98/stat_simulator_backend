from fastapi import APIRouter
import time
import random

from models.user import UserCreate
from models.monty_hist import MontyHallResultCreate

from .auth import register_user
from .dice_simul import roll_dice
from .monty_hall import record_monty_hall_result
from .anti_choice import anti_choose_number
from .admin import enable_dice_simulation, enable_monty_hall, enable_anti_choice, disable_all

# 테케 생성 등의 유틸 기능
router = APIRouter(tags=["Utility"])

# 학생들 등록하기
@router.post("/register_students")
async def register_students():
    for grade in range(1, 4):
        for stu_class in range(1, 3):
            for stu_num in range(1, 20):
                user_id = f"stu{grade}{stu_class}{str(stu_num).zfill(2)}" # stuYC## 형태
                nu = UserCreate(user_id=user_id, password=user_id, nickname=f"{grade}학년 {stu_class}반 {str(stu_num).zfill(2)}번")
                await register_user(nu)
     
    return {"message": "registration success"}


# 테스트 셋 생성
# 스트레스 테스트를 겸함
@router.post("/make_test_set")
async def make_test_set():
    print(await enable_dice_simulation(admin_id="admin"))
    print(await enable_monty_hall(admin_id="admin"))
    print(await enable_anti_choice(admin_id="admin"))

    start = time.time()
    for grade in range(1, 4):
        for stu_class in range(1, 3):
            for stu_num in range(1, 20):
                user_id = f"stu{grade}{stu_class}{str(stu_num).zfill(2)}"
                
                # dice roll 하기
                for _ in range(20):
                    await roll_dice(user_id=user_id, record=True)

                # 몬티홀 하기
                for _ in range(7):
                    my_change = random.randint(0, 1)
                    # 바꿨으면, 2/3 승률
                    if my_change:
                        my_win = random.choice([True, True, False])
                    # 아니면, 1/3 승률
                    else:
                        my_win = random.choice([True, False, False])
                    mrc = MontyHallResultCreate(user_id=user_id, change=my_change, win=my_win, record=True)
                    await record_monty_hall_result(mrc)
                
                # 번호 고르기
                my_pick = random.randint(0, 9)
                await anti_choose_number(user_id=user_id, anti_choice=my_pick)

    end = time.time()
    
    message = f"소요시간 : {end - start}초"
    print(await disable_all(admin_id="admin"))
    print(message)

    return {"message": message}