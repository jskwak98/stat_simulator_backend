from fastapi import APIRouter, HTTPException
from sqlalchemy.sql import func, select, case, join

from models.user import users
from models.dice_hist import dice_history
from models.monty_hist import monty_hall_history
from models.choice_hist import choice_history
from models.anti_choice_hist import anti_choice_history

from global_config import SUMS, MEAN, STD, NUM_SAMPLES

from database import database
from typing import Optional

router = APIRouter(tags=["Statistics"])


###### Dice Simul 관련 통계 ######

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

# 특정값이 나올 확률 계산해주기
@router.get("/get_dice_probs/{sum_rolls}")
async def get_dice_probs(sum_rolls: int):
    # 만약 평균 이하라면
    if sum_rolls <= MEAN:
        cnt = 0
        for val in SUMS:
            if sum_rolls >= val:
                cnt += 1
        return {"message": f"{sum_rolls} 이하로 나올 확률 -> {round(cnt / NUM_SAMPLES, 7) * 100}%",
                "mean" : MEAN,
                "std" : STD}
    else:
        cnt = 0
        for val in SUMS:
            if sum_rolls <= val:
                cnt += 1
        return {"message": f"{sum_rolls} 이상으로 나올 확률 -> {round(cnt / NUM_SAMPLES, 7) * 100}%",
                "mean" : MEAN,
                "std" : STD}
    

###### Monty Hall 관련 APIs ######

# 학생들의 전략 선택이 어땠는지 보여준다
@router.get("/get_strategy_stats")
async def get_strategy_stats(user_id: Optional[str] = None):
    # 바꿨는지 안 바꿨는지를 기반으로 Return
    query = select([
        func.sum(case([(monty_hall_history.c.change == True, 1)], else_=0)).label("changed"),
        func.sum(case([(monty_hall_history.c.change == False, 1)], else_=0)).label("not_changed")
    ])
    # 개인화 통계 표출용도
    if user_id:
        query = query.where(monty_hall_history.c.user_id == user_id)
    result = await database.fetch_one(query)
    return {"changed": result['changed'], "not_changed": result['not_changed']}

# 전략 선택에 따라서 얼마나 이겼는지 보여준다
@router.get("/get_win_stats")
async def get_win_stats(user_id: Optional[str] = None):
    # case별 승률과, case별 trial 수를 반환
    query = select([
        func.sum(case([(monty_hall_history.c.change == True, 1)], else_=0)).label("changed_wins"),
        func.count().filter(monty_hall_history.c.change == True).label("total_changed"),
        func.sum(case([(monty_hall_history.c.change == False, 1)], else_=0)).label("not_changed_wins"),
        func.count().filter(monty_hall_history.c.change == False).label("total_not_changed")
    ])
    # 개인화
    if user_id:
        query = query.where(monty_hall_history.c.user_id == user_id)
    result = await database.fetch_one(query)

    # 아직 시도가 없는 경우를 생각할 것
    return {
        "changed_win_rate": result['changed_wins'] / result['total_changed'] if result['total_changed'] else 0,
        "not_changed_win_rate": result['not_changed_wins'] / result['total_not_changed'] if result['total_not_changed'] else 0
    }

# 최고 최저 승률 학생들을 보여준다
@router.get("/winning_students")
async def winning_students():
    # subquery를 통해서 개별 승수를 뽑을 수 있게끔 한다
    subquery = select([
        monty_hall_history.c.user_id,
        func.count().filter(monty_hall_history.c.win == True).label("number_of_wins")
    ]).group_by(monty_hall_history.c.user_id).subquery()

    # 닉네임을 위해 user 테이블과 합침
    # 이후 승수에 따라 정렬
    query = select([
        users.c.user_id, users.c.nickname, subquery.c.number_of_wins
    ]).select_from(
        subquery.join(users, subquery.c.user_id == users.c.user_id)
    ).order_by(subquery.c.number_of_wins.desc())

    results = await database.fetch_all(query)

    # 최고 최저 승률 학생 return하기
    if not results:
        return {"best_students": [], "worst_students": []}
    
    max_wins = results[0].number_of_wins
    min_wins = results[-1].number_of_wins

    # 최고 최저 승수를 쌓은 학생들을 리스트에 넣어 반환하기
    best_students = [r for r in results if r.number_of_wins == max_wins]
    worst_students = [r for r in results if r.number_of_wins == min_wins]

    return {"best_students": best_students, "worst_students": worst_students}


###### Choice 관련 통계 ######

# 고른 통계를 히스토그램으로 표출
@router.get("/choice_frequency")
async def choice_frequency():
    # choice column을 groupby로 묶고 각자 count
    query = select([
        choice_history.c.choice, 
        func.count().label("count")
    ]).group_by(choice_history.c.choice)

    results = await database.fetch_all(query)
    # dict 형태로 변환
    frequency = {str(i): 0 for i in range(10)}
    for result in results:
        frequency[str(result.choice)] = result.count

    return frequency


###### Anti-Choice 관련 통계 ######

# 고른 통계를 히스토그램으로 표출
@router.get("/anti_choice_frequency")
async def anti_choice_frequency():
    # anti_choice column을 groupby로 묶고 각자 count
    query = select([
        anti_choice_history.c.anti_choice, 
        func.count().label("count")
    ]).group_by(anti_choice_history.c.anti_choice)

    results = await database.fetch_all(query)
    # dict 형태로 변환
    frequency = {str(i): 0 for i in range(10)}
    for result in results:
        frequency[str(result.anti_choice)] = result.count

    return frequency

# 각 숫자 별 유저 리스트
@router.get("/users_by_anti_choice/{number}")
async def users_by_anti_choice(number: int):
    if not 0 <= number <= 9:
        raise HTTPException(status_code=400, detail="Number must be between 0 and 9")

    # users와 join하고, 그 중 본인이 고른 숫자를 기준으로 select
    query = select([
        users.c.user_id, 
        users.c.nickname
    ]).select_from(
        anti_choice_history.join(users, anti_choice_history.c.user_id == users.c.user_id)
    ).where(anti_choice_history.c.anti_choice == number)

    results = await database.fetch_all(query)
    return [{"user_id": result.user_id, "nickname": result.nickname} for result in results]