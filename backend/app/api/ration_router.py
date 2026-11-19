from fastapi import APIRouter

from app.schemas import RationTargetCreate, RationOut
from app.services.ration_service import build_greedy_ration

router = APIRouter(prefix="/ration", tags=["Генератор рациона"])


@router.post("/generate", response_model=RationOut)
async def generate_ration(target: RationTargetCreate):
    return await build_greedy_ration(
        user_id=target.user_id,
        target_calories=target.target_calories,
    )

