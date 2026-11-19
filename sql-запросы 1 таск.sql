-- 1. Топ-5 самых калорийных продуктов
SELECT name, category, calories 
FROM products 
ORDER BY calories DESC 
LIMIT 5;

-- 2. Средняя калорийность по категориям
SELECT category, COUNT(*) as count_products, ROUND(AVG(calories), 2) as avg_calories 
FROM products 
GROUP BY category 
ORDER BY avg_calories DESC;

-- 3. Топ-3 бренда по количеству продуктов
SELECT brand, COUNT(*) as product_count 
FROM products 
WHERE brand IS NOT NULL AND brand != '' 
GROUP BY brand 
ORDER BY product_count DESC 
LIMIT 3;

-- 4. Продукты с высоким содержанием белка и низким жира
SELECT name, proteins, fats, calories 
FROM products 
WHERE proteins > 20 AND fats < 5 
ORDER BY proteins DESC;

-- 5. Оконная функция: Ранжирование по калорийности внутри категории
SELECT 
    name, 
    category, 
    calories,
    RANK() OVER (PARTITION BY category ORDER BY calories DESC) as rank_in_category
FROM products;