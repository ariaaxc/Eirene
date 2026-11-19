from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import session_factory
from app.models import Receipt
from app.schemas import ReceiptOut
from app.services.receipts_service import move_receipt_items_to_fridge, generate_receipts_csv

router = APIRouter(prefix="/receipts", tags=["Чеки и покупки"])


@router.get("/{user_id}", response_model=list[ReceiptOut])
async def get_user_receipts(user_id: int):
    async with session_factory() as session:
        query = (
            select(Receipt)
            .where(Receipt.user_id == user_id)
            .options(selectinload(Receipt.items))
            .order_by(Receipt.purchased_at.desc())
        )
        result = await session.execute(query)
        return result.scalars().all()


@router.post("/{receipt_id}/sync-fridge")
async def sync_receipt_to_fridge(receipt_id: int, user_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(move_receipt_items_to_fridge, receipt_id, user_id)
    return {"message": "Перенос продуктов в холодильник запущен в фоне"}


@router.get("/{user_id}/export")
async def export_user_receipts_csv(user_id: int):
    headers = {"Content-Disposition": f'attachment; filename="receipts_user_{user_id}.csv"'}
    return StreamingResponse(generate_receipts_csv(user_id), media_type="text/csv", headers=headers)
