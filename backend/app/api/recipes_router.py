from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.base import Recipe, UserFridge, RecipeIngredient, Product
from app.schemas.recipes import RecipeShort, RecipeDetailed
from app.services.fridge_service import get_expiring_product_ids

router = APIRouter(prefix="/api/recipes", tags=["Каталог рецептов"])

# 1. Каталог рецептов с пагинацией (из базы данных)
@router.get("", response_model=List[RecipeShort])
def get_recipes_catalog(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    recipes = db.query(Recipe).offset(skip).limit(limit).all()
    return recipes

# 2. Подробный рецепт (из базы данных)
@router.get("/{recipe_id}", response_model=RecipeDetailed)
def get_recipe_detail(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return recipe

# 3. ВАУ-ФИЧА: Что можно приготовить из холодильника (Task 2.4)
# Мы берем реальный холодильник пользователя из БД и сравниваем с ингредиентами рецептов.
@router.get("/what-to-cook/{user_id}")
def what_to_cook(user_id: int, db: Session = Depends(get_db)):
    # 1. Достаем все продукты, которые сейчас в холодильнике у пользователя
    fridge_items = db.query(UserFridge).filter(UserFridge.user_id == user_id).all()
    
    if not fridge_items:
        return {"message": "Ваш холодильник пуст"}

    # Получаем ID продуктов из холодильника
    fridge_product_ids = [item.product_id for item in fridge_items]
    
    # 2. Достаем все рецепты
    all_recipes = db.query(Recipe).all()
    matching_recipes = []
    
    # 3. Проверяем каждый рецепт
    for recipe in all_recipes:
        # Получаем все ингредиенты для этого рецепта
        recipe_ingredients = db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe.id).all()
        
        # Узнаем ID продуктов, которые нужны для рецепта
        needed_product_ids = [ing.product_id for ing in recipe_ingredients]
        
        if not needed_product_ids:
            continue
            
        # Проверяем, какие есть в холодильнике, а каких нет
        available = [pid for pid in needed_product_ids if pid in fridge_product_ids]
        missing = [pid for pid in needed_product_ids if pid not in fridge_product_ids]
        
        matching_recipes.append({
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "can_cook": len(missing) == 0, # Если ничего не не хватает - можно готовить!
            "available_ingredients_count": len(available),
            "missing_ingredients_count": len(missing),
            "missing_product_ids": missing # Фронтенд сможет подсветить, чего не хватает
        })
    
    # Сортируем: сначала те, что можно приготовить прямо сейчас
    matching_recipes.sort(key=lambda x: x["can_cook"], reverse=True)
    
    # 4. ПОЛУЧАЕМ ПРОДУКТЫ, КОТОРЫЕ СКОРО ИСПОРТЯТСЯ
    expiring_ids = get_expiring_product_ids(user_id, db)
    
    # Добавляем информацию о просрочке в ответ
    return {
        "user_id": user_id,
        "expiring_soon_product_ids": expiring_ids, # <-- Настя Г. будет это использовать
        "total_recipes_checked": len(all_recipes),
        "results": matching_recipes
    }

    return {
        "user_id": user_id,
        "total_recipes_checked": len(all_recipes),
        "results": matching_recipes
    }