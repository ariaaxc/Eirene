import asyncio
import csv
from pathlib import Path
from sqlalchemy import select

from backend.app.core.database import session_factory, engine
from backend.app.models import Product



async def seed_products() -> None:
    csv_path = Path(__file__).parent / "products.csv"
    if not csv_path.exists():
        print(f"Файл {csv_path} не найден!")
        return

    async with session_factory() as session:
        result = await session.execute(select(Product.name))
        existing_names = set(result.scalars().all())

        new_products = []
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"].strip()
                if not name or name in existing_names:
                    continue

                product = Product(
                    name=name,
                    category=row["category"].strip(),
                    proteins=float(row.get("proteins") or 0),
                    fats=float(row.get("fats") or 0),
                    carbs=float(row.get("carbs") or 0),
                    calories=float(row.get("calories") or 0),
                    shelf_life_days=int(row["shelf_life_days"]) if row.get("shelf_life_days") else None,
                    health_score=int(row["health_score"]) if row.get("health_score") else None,
                )
                new_products.append(product)
                existing_names.add(name)

        if new_products:
            session.add_all(new_products)
            await session.commit()
            print(f"Успешно добавлено продуктов: {len(new_products)}")
        else:
            print("Новых продуктов для добавления нет.")


    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_products())
