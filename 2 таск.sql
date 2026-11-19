USE eirene;
ALTER TABLE user_fridge ADD COLUMN expiration_date DATE;
ALTER TABLE receipt_items ADD COLUMN price FLOAT;
INSERT INTO users (id, username, email, password_hash)  VALUES (1, 'testuser', 'test@test.com', 'testpassword');
SELECT * FROM products WHERE id=1;