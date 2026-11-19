from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import session_factory
from app.models import MealLog, Product
from app.schemas import MealLogCreate, MealLogOut

router = APIRouter(prefix="/meals", tags=["Приемы пищи"])


# Вспомогательная функция: пересчитывает КБЖУ продукта на съеденную граммовку
def build_meal_out(meal: MealLog, product: Product) -> MealLogOut:
    ratio = float(meal.quantity) / 100.0  # БЖУ в справочнике указано на 100 г
    return MealLogOut(
        id=meal.id,
        user_id=meal.user_id,
        product_id=meal.product_id,
        quantity=float(meal.quantity),
        meal_type=meal.meal_type,
        eaten_at=meal.eaten_at,
        total_calories=round(float(product.calories) * ratio, 1),
        total_proteins=round(float(product.proteins) * ratio, 1),
        total_fats=round(float(product.fats) * ratio, 1),
        total_carbs=round(float(product.carbs) * ratio, 1),
    )


@router.post("", response_model=MealLogOut)
async def create_meal(data: MealLogCreate):
    async with session_factory() as session:
        product = await session.get(Product, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")

        new_meal = MealLog(
            user_id=data.user_id,
            product_id=data.product_id,
            quantity=data.quantity,
            meal_type=data.meal_type,
            eaten_at=datetime.now(),
        )
        session.add(new_meal)
        await session.commit()
        await session.refresh(new_meal)

        return build_meal_out(new_meal, product)


@router.get("")
async def get_daily_meals(user_id: int):
    async with session_factory() as session:
        query = (
            select(MealLog)
            .where(MealLog.user_id == user_id, func.date(MealLog.eaten_at) == date.today())
            .options(selectinload(MealLog.product))
            .order_by(MealLog.eaten_at.desc())
        )
        result = await session.execute(query)
        meals = result.scalars().all()

        items = [build_meal_out(m, m.product) for m in meals]

        # Суммарное КБЖУ за весь день
        summary = {
            "calories": round(sum(i.total_calories for i in items), 1),
            "proteins": round(sum(i.total_proteins for i in items), 1),
            "fats": round(sum(i.total_fats for i in items), 1),
            "carbs": round(sum(i.total_carbs for i in items), 1),
        }

        return {"meals": items, "summary_kbzhu": summary}
