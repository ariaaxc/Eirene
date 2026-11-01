from fastapi import APIRouter, Query
from typing import List

router = APIRouter(prefix="/recipes", tags=["Каталог рецептов"])

# 1. каталог рецептов, с точным списком нужных ингредиентов!
FAKE_RECIPES_DATABASE = [
    {
        "id": 1,
        "name": "Борщ",
        "ingredients": ["свекла", "капуста", "мясо", "картошка", "лук"]
    },
    {
        "id": 2,
        "name": "Яичница с луком",
        "ingredients": ["яйцо", "лук", "масло"]
    },
    {
        "id": 3,
        "name": "Курица с рисом",
        "ingredients": ["курица", "рис", "лук"]
    }
]


#  эндпоинт с пагинацией
@router.get("")
async def get_recipes_catalog(page: int = 1, limit: int = 2):
    start_index = (page - 1) * limit
    end_index = start_index + limit
    return {"recipes": FAKE_RECIPES_DATABASE[start_index:end_index]}


# 2. ЭНДПОИНТ: Проверка продуктов из холодильника (GET /api/recipes/check-fridge)
@router.get("/check-fridge")
async def check_fridge_ingredients(fridge: List[str] = Query(default=[])):

    fridge_products = [p.lower() for p in fridge]

    results = []


    for recipe in FAKE_RECIPES_DATABASE:
        recipe_ingredients = recipe["ingredients"]


        available = [item for item in recipe_ingredients if item in fridge_products]

        missing = [item for item in recipe_ingredients if item not in fridge_products]

        results.append({
            "recipe_name": recipe["name"],
            "all_needed_ingredients": recipe_ingredients,
            "what_you_have": available,
            "what_is_missing": missing,
            "can_cook": len(missing) == 0
        })

    return {
        "your_fridge": fridge_products,
        "matching_results": results
    }
