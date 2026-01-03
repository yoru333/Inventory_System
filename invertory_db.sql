Create database inventory_db;
USE inventory_db;
-- 商品表
Create table products(
product_id INT PRIMARY KEY AUTO_INCREMENT,
name VARCHAR(100) NOT NULL,
category VARCHAR(50),
unit_price DECIMAL(10, 2),
stock INT DEFAULT 0,
safe_stock INT DEFAULT 10
);

-- 進貨表
Create table stock_in(
in_id INT PRIMARY KEY AUTO_INCREMENT,
product_id INT,
quantity INT,
in_date DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(product_id) REFERENCES products(product_id)
); 

-- 銷售表
Create table stock_out(
out_id INT PRIMARY KEY AUTO_INCREMENT,
product_id INT,
quantity INT,
out_date DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(product_id) REFERENCES products(product_id)
); 