USE livecart;

INSERT INTO customers (full_name, email, city) VALUES
('Aarav Sharma','aarav.sharma@example.com','Hyderabad'),
('Diya Reddy','diya.reddy@example.com','Visakhapatnam'),
('Arjun Kumar','arjun.kumar@example.com','Bengaluru'),
('Ananya Rao','ananya.rao@example.com','Chennai'),
('Vikram Patel','vikram.patel@example.com','Mumbai'),
('Meera Iyer','meera.iyer@example.com','Pune'),
('Rohan Das','rohan.das@example.com','Kolkata'),
('Saanvi Gupta','saanvi.gupta@example.com','Delhi'),
('Ishaan Verma','ishaan.verma@example.com','Hyderabad'),
('Kavya Nair','kavya.nair@example.com','Vizianagaram')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), city=VALUES(city);

INSERT INTO products (product_name, category, unit_price, stock_quantity) VALUES
('Wireless Mouse','Electronics',799.00,80),
('Mechanical Keyboard','Electronics',2499.00,35),
('USB-C Hub','Electronics',1799.00,24),
('Cotton T-Shirt','Fashion',599.00,100),
('Running Shoes','Fashion',3299.00,18),
('Water Bottle','Home',399.00,120),
('Desk Lamp','Home',1199.00,28),
('Notebook Set','Stationery',249.00,200),
('Backpack','Fashion',1499.00,15),
('Bluetooth Speaker','Electronics',2199.00,20)
ON DUPLICATE KEY UPDATE unit_price=VALUES(unit_price), stock_quantity=VALUES(stock_quantity);

-- Sample orders are added by seed_data.py so dates remain relative to the run date.
