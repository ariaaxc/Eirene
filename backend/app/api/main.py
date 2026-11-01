from fastapi import FastAPI
import uvicorn

from app.api.meals_router import router as meals_router
from app.api.recipes_router import router as recipes_router

app = FastAPI(title="Дневник питания и рецептов")

app.include_router(meals_router, prefix="/api")

app.include_router(recipes_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Бэкенд-сервер Eirene успешно запущен и работает!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
