from fastapi import APIRouter
from app.services.meals_service import calculate_total_kbzhu

# Создаем роутер
router = APIRouter(prefix="/meals", tags=["Приемы пищи"])


@router.post("")
async def create_meal():
    return {"message": "Прием пищи успешно записан!"}



@router.get("")
async def get_daily_meals():
    #  фейковая база данных
    fake_meals_db = [
        {"name": "Овсянка", "calories": 300, "proteins": 10, "fats": 5, "carbs": 50},
        {"name": "Курица с рисом", "calories": 500, "proteins": 40, "fats": 10, "carbs": 60}
    ]

    # Передаем список еды в калькулятор, который лежит в meals_service
    summary = calculate_total_kbzhu(fake_meals_db)

    return {
        "meals": fake_meals_db,
        "summary_kbzhu": summary
    }
