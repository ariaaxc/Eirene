from fastapi import FastAPI
from app.api import products_router, fridge_router
from app.api import receipts_router
from app.api import notifications_router

app = FastAPI()

# Тут может быть твой код с meals_router и recipes_router...
# app.include_router(meals_router.router)

app.include_router(products_router.router)
app.include_router(fridge_router.router)
app.include_router(receipts_router.router)
app.include_router(notifications_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
