import csv
from sqlalchemy import create_engine, text

DB_URL = "mysql+pymysql://root:1029384756Aa@localhost:3306/eirene"
engine = create_engine(DB_URL)

def seed():
    try:
        with open('products.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Пропускаем заголовки
            
            with engine.begin() as conn:
                count = 0
                for row in reader:
                    if len(row) < 22: continue
                    
                    def num(val):
                        try:
                            return float(val.replace(',', '.')) if val.strip() else 0.0
                        except:
                            return 0.0

                    # ID мы теперь не передаем, база сама поставит 1, 2, 3...
                    query = text("""
                        INSERT INTO products (name, category, brand, manufacturer, price, proteins, fats, carbs, calories, sugar, salt, cholesterol, nitrites, allergens, ingredients, shelf_life_days, health_score)
                        VALUES (:name, :category, :brand, :manufacturer, :price, :proteins, :fats, :carbs, :calories, :sugar, :salt, :cholesterol, :nitrites, :allergens, :ingredients, :shelf_life_days, :health_score)
                    """)
                    
                    conn.execute(query, {
                        "name": row[0], 
                        "category": row[1], 
                        "brand": row[20] if len(row) > 20 else None, 
                        "manufacturer": row[20] if len(row) > 20 else None,
                        "price": num(row[2]),
                        "proteins": num(row[4]), 
                        "fats": num(row[5]), 
                        "carbs": num(row[6]), 
                        "calories": num(row[3]), 
                        "sugar": num(row[9]), 
                        "salt": num(row[10]), 
                        "cholesterol": num(row[13]), 
                        "nitrites": num(row[11]), 
                        "allergens": row[8] if row[8] else None, 
                        "ingredients": row[16] if row[16] else None, 
                        "shelf_life_days": int(num(row[18]) / 24), 
                        "health_score": 0.0 
                    })
                    count += 1
        print(f"🎉 УСПЕХ! Загружено {count} продуктов с числовыми ID.")
    except Exception as e:
        print("❌ Ошибка:", e)

if __name__ == "__main__":
    seed()