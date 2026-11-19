from datetime import date
from sqlalchemy import select

from app.core.database import session_factory
from app.models import Receipt, ReceiptItem, UserFridge

# Фоновая задача: перекидываем продукты из чека в холодильник
async def move_receipt_items_to_fridge(receipt_id: int, user_id: int):
    async with session_factory() as session:
        query = select(ReceiptItem).where(
            ReceiptItem.receipt_id == receipt_id,
            ReceiptItem.product_id.is_not(None),
        )
        result = await session.execute(query)
        items = result.scalars().all()

        for item in items:
            session.add(
                UserFridge(
                    user_id=user_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    added_date=date.today(),
                    price=item.price,
                )
            )

        await session.commit()

# Генератор CSV: отдаем историю покупок по одной строчке
async def generate_receipts_csv(user_id: int):
    yield "\ufeffДата покупки;Магазин;Товар;Количество;Цена\n"

    async with session_factory() as session:
        query = (
            select(
                Receipt.purchased_at,
                Receipt.store_name,
                ReceiptItem.raw_name,
                ReceiptItem.quantity,
                ReceiptItem.price,
            )
            .join(ReceiptItem, Receipt.id == ReceiptItem.receipt_id)
            .where(Receipt.user_id == user_id)
            .order_by(Receipt.purchased_at.desc())
        )
        result = await session.stream(query)
        async for row in result:
            date_str = row.purchased_at.strftime("%Y-%m-%d %H:%M")
            store = row.store_name or "Не указан"
            yield f"{date_str};{store};{row.raw_name};{row.quantity};{row.price}\n"
