-- Полностью удаляем старую базу (это снимает все блокировки ключей)
DROP DATABASE IF EXISTS eirene;
CREATE DATABASE eirene CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eirene;

-- 1. Пользователи
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Продукты (ТЕПЕРЬ С ЧИСЛОВЫМ ID)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    brand VARCHAR(255),
    manufacturer VARCHAR(255),
    price FLOAT DEFAULT 0,
    proteins FLOAT DEFAULT 0,
    fats FLOAT DEFAULT 0,
    carbs FLOAT DEFAULT 0,
    calories FLOAT DEFAULT 0,
    sugar FLOAT DEFAULT 0,
    salt FLOAT DEFAULT 0,
    cholesterol FLOAT DEFAULT 0,
    nitrites FLOAT DEFAULT 0,
    allergens TEXT,
    ingredients TEXT,
    shelf_life_days INT DEFAULT 0,
    health_score FLOAT DEFAULT 0
);

-- 3. Настройки пользователя
CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_calories FLOAT,
    target_proteins FLOAT,
    target_fats FLOAT,
    target_carbs FLOAT,
    telegram_chat_id VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Холодильник
CREATE TABLE user_fridge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity FLOAT NOT NULL,
    added_date DATE,
    price FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 5. Дневник питания
CREATE TABLE meal_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity FLOAT NOT NULL,
    meal_type VARCHAR(255),
    eaten_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 6. Чеки
CREATE TABLE receipts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount FLOAT NOT NULL,
    store_name VARCHAR(255),
    purchased_at DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Позиции в чеке
CREATE TABLE receipt_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receipt_id INT NOT NULL,
    product_id INT,
    raw_name VARCHAR(255),
    quantity FLOAT,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 8. Рецепты
CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id INT,
    name VARCHAR(255) NOT NULL,
    instructions TEXT,
    calories FLOAT DEFAULT 0,
    proteins FLOAT DEFAULT 0,
    fats FLOAT DEFAULT 0,
    carbs FLOAT DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 9. Ингредиенты рецептов
CREATE TABLE recipe_ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity FLOAT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 10. Уведомления
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
