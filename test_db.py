import psycopg2

# Подключение к базе
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="vkus_kontrolya",
    user="postgres",
    password="secret"
)

cur = conn.cursor()

# Выполняем запрос: получаем все продукты
cur.execute("SELECT id, name, proteins, fats, carbs, calories FROM products;")
rows = cur.fetchall()

# Выводим результаты
for row in rows:
    print(f"{row[1]}: {row[2]}г белков, {row[3]}г жиров, {row[4]}г углеводов, {row[5]} ккал")

cur.close()
conn.close()