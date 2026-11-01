def calculate_total_kbzhu(meals: list) -> dict:
    total_calories = 0
    total_proteins = 0
    total_fats = 0
    total_carbs = 0

    for meal in meals:
        total_calories += meal.get("calories", 0)
        total_proteins += meal.get("proteins", 0)
        total_fats += meal.get("fats", 0)
        total_carbs += meal.get("carbs", 0)

    return {
        "calories": total_calories,
        "proteins": total_proteins,
        "fats": total_fats,
        "carbs": total_carbs
    }