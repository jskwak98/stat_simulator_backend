from fastapi import APIRouter, HTTPException, Query
from global_config import simulations_config

router = APIRouter(tags=["Admin"])

@router.post("/admin/enable_dice")
async def enable_dice_simulation(admin_id: str = Query(default="admin", description="Admin ID")):
    if admin_id != "admin":
        raise HTTPException(status_code=403, detail="Admin만 통제가 가능해요!")
    simulations_config["dice_enabled"] = True
    return {"message": "주사위 로또! 기능이 켜졌습니다"}

@router.post("/admin/enable_monty_hall")
async def enable_monty_hall(admin_id: str = Query(default="admin", description="Admin ID")):
    if admin_id != "admin":
        raise HTTPException(status_code=403, detail="Admin만 통제가 가능해요!")
    simulations_config["monty_hall_enabled"] = True
    return {"message": "몬티 홀 기능이 켜졌습니다"}

@router.post("/admin/enable_choice")
async def enable_choice(admin_id: str = Query(default="admin", description="Admin ID")):
    if admin_id != "admin":
        raise HTTPException(status_code=403, detail="Admin만 통제가 가능해요!")
    simulations_config["choice_enabled"] = True
    return {"message": "숫자 고르기 기능이 켜졌습니다"}

@router.post("/admin/enable_anti_choice")
async def enable_anti_choice(admin_id: str = Query(default="admin", description="Admin ID")):
    if admin_id != "admin":
        raise HTTPException(status_code=403, detail="Admin만 통제가 가능해요!")
    simulations_config["anti_choice_enabled"] = True
    return {"message": "숫자 몰래 고르기 기능이 켜졌습니다"}

@router.post("/admin/disable_all")
async def disable_all(admin_id: str = Query(default="admin", description="Admin ID")):
    if admin_id != "admin":
        raise HTTPException(status_code=403, detail="Admin만 통제가 가능해요!")
    simulations_config["anti_choice_enabled"] = False
    simulations_config["dice_enabled"] = False
    simulations_config["monty_hall_enabled"] = False
    simulations_config["choice_enabled"] = False
    return {"message": "모든 기능을 껐습니다."}