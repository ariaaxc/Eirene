from fastapi import APIRouter
from sqlalchemy import select, func, and_, text
from sqlalchemy.orm import selectinload

from app.core.database import session_factory
from app.models import Recipe, RecipeIngredient, UserFridge, Product
from app.schemas import RecipeOut, WhatToCookOut

router = APIRouter(prefix="/recipes", tags=["Каталог рецептов"])


# 1. Каталог рецептов с пагинацией
@router.get("", response_model=list[RecipeOut])
async def get_recipes_catalog(page: int = 1, limit: int = 10):
    async with session_factory() as session:
        query = select(Recipe).options(selectinload(Recipe.ingredients)).offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()


# 2. Что приготовить: приоритет по продуктам с истекающим сроком годности
@router.get("/what-to-cook", response_model=list[WhatToCookOut])
async def get_what_to_cook(user_id: int, only_ready: bool = False):
    async with session_factory() as session:
        total_cnt = func.count(RecipeIngredient.product_id)
        avail_cnt = func.count(UserFridge.id)

        # Считаем дату просрочки (дата добавления + срок годности) и берем самую ближайшую
        exp_date = func.date_add(UserFridge.added_date, text("INTERVAL products.shelf_life_days DAY"))
        earliest_exp = func.min(exp_date)

        # Условие, что продукт есть в холодильнике в нужном количестве
        has_product = and_(
            UserFridge.product_id == RecipeIngredient.product_id,
            UserFridge.user_id == user_id,
            UserFridge.quantity >= RecipeIngredient.quantity,
        )

        query = (
            select(
                Recipe.id, Recipe.name, Recipe.instructions, Recipe.calories,
                total_cnt.label("total_ingredients"),
                avail_cnt.label("available_ingredients"),
                earliest_exp.label("earliest_expiration"),
            )
            .join(RecipeIngredient, Recipe.id == RecipeIngredient.recipe_id)
            .join(Product, Product.id == RecipeIngredient.product_id)
            .outerjoin(UserFridge, has_product)
            .group_by(Recipe.id)
            .order_by(avail_cnt.desc(), earliest_exp.is_(None), earliest_exp.asc())
        )

        if only_ready:
            query = query.having(and_(total_cnt == avail_cnt))

        result = await session.execute(query)
        return result.all()
