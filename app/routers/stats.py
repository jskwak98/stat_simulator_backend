from fastapi import APIRouter
from sqlalchemy.sql import func, select, case, join

from models.user import users
from models.dice_hist import dice_history
from models.monty_hist import monty_hall_history
from models.choice_hist import choice_history
from models.anti_choice_hist import anti_choice_history

from global_config import SUMS, MEAN, STD

from database import database
from typing import Optional

router = APIRouter()

# 전체 그룹 dice_histogram
# /dice_histogram?user_id=some_user_id 로 부르면 특정 유저의 결과가 나온다.
@router.get("/dice_histogram")
async def dice_histogram(user_id: Optional[str] = None):
    # 50 단위로 표현할 것
    ranges = [
        (6, 50), (51, 100), (101, 150), (151, 200), 
        (201, 250), (251, 300), (301, 350), (351, 400),
        (401, 450), (451, 500), (501, 550), (551, 600)
    ]
    
    # case 문을 통한 count
    sum_cases = [func.sum(case([(dice_history.c.sum_of_rolls.between(low, high), 1)], else_=0)).label(f'{low}~{high}') for low, high in ranges]

    # 개인화할건지 다 함께인지
    if user_id:
        query = select(sum_cases).where(dice_history.c.user_id == user_id)
    else:
        query = select(sum_cases)

    # 실제로 실행
    query = select(sum_cases)
    result = await database.fetch_one(query)
    
    # 데이터 반환
    histogram_data = {f'{low}~{high}': result[f'{low}~{high}'] for low, high in ranges}
    return histogram_data

# 가장 큰 top 3, 가장 작은 top 3를 선정함
@router.get("/top_dice_rolls")
async def top_dice_rolls(user_id: Optional[str] = None):
    # 닉네임도 사용할 예정이므로 join해준다.
    joined_table = join(dice_history, users, dice_history.c.user_id == users.c.user_id)

    # 가장 큰 3개의 roll 찾기
    top_query = select([dice_history.c.sum_of_rolls, dice_history.c.rolls, users.c.user_id, users.c.nickname])\
                .select_from(joined_table)\
                .order_by(dice_history.c.sum_of_rolls.desc())\
                .limit(3)
    if user_id:
        top_query = top_query.where(dice_history.c.user_id == user_id)

    top_rolls = await database.fetch_all(top_query)

    # 가장 작은 3개의 roll 찾기
    bottom_query = select([dice_history.c.sum_of_rolls, dice_history.c.rolls, users.c.user_id, users.c.nickname])\
                   .select_from(joined_table)\
                   .order_by(dice_history.c.sum_of_rolls)\
                   .limit(3)
    if user_id:
        bottom_query = bottom_query.where(dice_history.c.user_id == user_id)

    bottom_rolls = await database.fetch_all(bottom_query)

    return {"top_rolls": top_rolls, "bottom_rolls": bottom_rolls}

# 가장 Rare하게 굴린 3명을 정규화를 통해서 선정할 것
@router.get("/rarest_rolls")
async def rarest_rolls():
    # Roll Data를 가져오기
    query = select([dice_history.c.sum_of_rolls, dice_history.c.user_id])
    rolls_data = await database.fetch_all(query)

    # 정규화 하기
    normalized_rolls = [(user_id, sum_of_rolls, abs((sum_of_rolls - MEAN) / STD)) for sum_of_rolls, user_id in rolls_data]

    # 유저 별로 top 3를 뽑아주기
    user_scores = {}
    for user_id, sum_of_rolls, norm_roll in normalized_rolls:
        user_scores.setdefault(user_id, []).append((sum_of_rolls, norm_roll))
        user_scores[user_id] = sorted(user_scores[user_id], key=lambda x: x[1], reverse=True)[:3]

    # 점수 계산하기
    user_total_scores = {user_id: (sum(score for _, score in rolls), rolls) for user_id, rolls in user_scores.items()}

    # 다시 재정렬 하고 top 3 뽑기
    sorted_users = sorted(user_total_scores.items(), key=lambda x: x[1][0], reverse=True)[:3]

    # 포맷팅해서 반환하기
    top_users_with_rolls = [
        {"user_id": user_id, "total_score": total_score, "top_rolls": [{"roll": roll, "score": score} for roll, score in rolls]}
        for user_id, (total_score, rolls) in sorted_users
    ]

    return {"top_3_users": top_users_with_rolls}