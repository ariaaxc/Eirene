from datetime import date
from sqlalchemy import select, func

from app.core.database import session_factory
from app.models import MealLog, Product, Recipe


async def build_greedy_ration(user_id: int, target_calories: float):
    async with session_factory() as session:
        # 1. Считаем, сколько калорий юзер уже наел за сегодня
        eaten_query = (
            select(func.sum(Product.calories * (MealLog.quantity / 100.0)))
            .join(Product, MealLog.product_id == Product.id)
            .where(MealLog.user_id == user_id, func.date(MealLog.eaten_at) == date.today())
        )
        eaten_result = await session.execute(eaten_query)
        eaten_calories = float(eaten_result.scalar() or 0.0)

        # 2. Вычисляем остаточный дефицит на день
        remaining_calories = max(0.0, target_calories - eaten_calories)

        # 3. Берем все рецепты с известной калорийностью и сортируем от самых сытных к легким
        recipes_query = (
            select(Recipe)
            .where(Recipe.calories.is_not(None), Recipe.calories > 0)
            .order_by(Recipe.calories.desc())
        )
        recipes_result = await session.execute(recipes_query)
        recipes = recipes_result.scalars().all()

        # 4. Кладем в рацион всё, что влезает в остаток калорий
        selected_recipes = []
        ration_calories = 0.0
        left_to_fill = remaining_calories

        for recipe in recipes:
            cal = float(recipe.calories)
            if cal <= left_to_fill:
                selected_recipes.append(recipe.name)
                ration_calories += cal
                left_to_fill -= cal

        return {
            "target_calories": target_calories,
            "eaten_today": round(eaten_calories, 1),
            "remaining_deficit": round(remaining_calories, 1),
            "ration_calories": round(ration_calories, 1),
            "recipes": selected_recipes,
        }
