CREATE DATABASE IF NOT EXISTS livecart
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE livecart;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    city VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE KEY uq_product_name (product_name),
    CONSTRAINT chk_product_price CHECK (unit_price >= 0),
    CONSTRAINT chk_stock CHECK (stock_quantity >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    status ENUM('Pending','Processing','Shipped','Delivered','Cancelled','Refunded')
        NOT NULL DEFAULT 'Pending',
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipping_city VARCHAR(100) NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    INDEX idx_orders_date (order_date),
    INDEX idx_orders_status_date (status, order_date),
    INDEX idx_orders_customer (customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_items_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product FOREIGN KEY (product_id)
        REFERENCES products(product_id),
    CONSTRAINT chk_item_quantity CHECK (quantity > 0),
    CONSTRAINT chk_item_price CHECK (unit_price >= 0),
    INDEX idx_items_product (product_id),
    INDEX idx_items_order (order_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    payment_method ENUM('Card','UPI','Net Banking','Cash on Delivery') NOT NULL,
    payment_status ENUM('Pending','Paid','Failed','Refunded') NOT NULL DEFAULT 'Pending',
    amount DECIMAL(12,2) NOT NULL,
    paid_at DATETIME NULL,
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE,
    INDEX idx_payments_status (payment_status)
);

-- Helpful reporting view. Revenue includes orders that are shipped or delivered.
CREATE OR REPLACE VIEW vw_order_summary AS
SELECT
    o.order_id,
    o.order_date,
    o.status,
    c.customer_id,
    c.full_name AS customer_name,
    c.email,
    o.shipping_city,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS order_total
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.order_date, o.status, c.customer_id,
         c.full_name, c.email, o.shipping_city;
