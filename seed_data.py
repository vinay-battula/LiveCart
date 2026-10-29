from datetime import datetime, timedelta
import random

from db import get_connection

random.seed(21)

CUSTOMERS = [
    ("Aarav Sharma", "aarav.sharma@example.com", "Hyderabad"),
    ("Diya Reddy", "diya.reddy@example.com", "Visakhapatnam"),
    ("Arjun Kumar", "arjun.kumar@example.com", "Bengaluru"),
    ("Ananya Rao", "ananya.rao@example.com", "Chennai"),
    ("Vikram Patel", "vikram.patel@example.com", "Mumbai"),
    ("Meera Iyer", "meera.iyer@example.com", "Pune"),
    ("Rohan Das", "rohan.das@example.com", "Kolkata"),
    ("Saanvi Gupta", "saanvi.gupta@example.com", "Delhi"),
    ("Ishaan Verma", "ishaan.verma@example.com", "Hyderabad"),
    ("Kavya Nair", "kavya.nair@example.com", "Vizianagaram"),
]
PRODUCTS = [
    ("Wireless Mouse", "Electronics", 799.00, 80),
    ("Mechanical Keyboard", "Electronics", 2499.00, 35),
    ("USB-C Hub", "Electronics", 1799.00, 24),
    ("Cotton T-Shirt", "Fashion", 599.00, 100),
    ("Running Shoes", "Fashion", 3299.00, 18),
    ("Water Bottle", "Home", 399.00, 120),
    ("Desk Lamp", "Home", 1199.00, 28),
    ("Notebook Set", "Stationery", 249.00, 200),
    ("Backpack", "Fashion", 1499.00, 15),
    ("Bluetooth Speaker", "Electronics", 2199.00, 20),
]
STATUSES = ["Delivered", "Delivered", "Delivered", "Shipped", "Processing", "Pending", "Cancelled"]
METHODS = ["Card", "UPI", "Net Banking", "Cash on Delivery"]


def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.executemany(
            """INSERT INTO customers (full_name,email,city) VALUES (%s,%s,%s)
               ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), city=VALUES(city)""",
            CUSTOMERS,
        )
        cur.executemany(
            """INSERT INTO products (product_name,category,unit_price,stock_quantity)
               VALUES (%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE category=VALUES(category),
                 unit_price=VALUES(unit_price), stock_quantity=VALUES(stock_quantity)""",
            PRODUCTS,
        )
        conn.commit()

        cur.execute("SELECT customer_id, city FROM customers ORDER BY customer_id")
        customers = cur.fetchall()
        cur.execute("SELECT product_id, unit_price FROM products ORDER BY product_id")
        products = cur.fetchall()

        # Add sample orders only if the database currently has none.
        cur.execute("SELECT COUNT(*) FROM orders")
        existing = cur.fetchone()[0]
        if existing == 0:
            now = datetime.now()
            for _ in range(60):
                customer_id, city = random.choice(customers)
                status = random.choice(STATUSES)
                order_date = now - timedelta(
                    days=random.randint(0, 29),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                cur.execute(
                    "INSERT INTO orders (customer_id,status,order_date,shipping_city) VALUES (%s,%s,%s,%s)",
                    (customer_id, status, order_date, city),
                )
                order_id = cur.lastrowid
                chosen = random.sample(products, k=random.randint(1, 3))
                total = 0.0
                for product_id, unit_price in chosen:
                    quantity = random.randint(1, 3)
                    price = float(unit_price)
                    total += quantity * price
                    cur.execute(
                        "INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (%s,%s,%s,%s)",
                        (order_id, product_id, quantity, price),
                    )
                pay_status = "Refunded" if status == "Refunded" else (
                    "Paid" if status in ("Shipped", "Delivered") else "Pending"
                )
                if status == "Cancelled":
                    pay_status = "Failed"
                cur.execute(
                    """INSERT INTO payments (order_id,payment_method,payment_status,amount,paid_at)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (order_id, random.choice(METHODS), pay_status, round(total, 2),
                     order_date if pay_status == "Paid" else None),
                )
            conn.commit()
            print("Inserted 60 sample orders.")
        else:
            print(f"Found {existing} existing orders; left them unchanged.")
        print("Seed data is ready.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
