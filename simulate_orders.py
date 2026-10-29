"""Insert one random order to simulate a new order arriving in the store."""
import random
from datetime import datetime

from db import get_connection

METHODS = ["Card", "UPI", "Net Banking", "Cash on Delivery"]


def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT customer_id, city FROM customers ORDER BY customer_id")
        customers = cur.fetchall()
        cur.execute("SELECT product_id, unit_price, stock_quantity FROM products WHERE active=TRUE")
        products = [p for p in cur.fetchall() if p[2] > 0]
        if not customers or not products:
            raise RuntimeError("Run seed_data.py first so customers and products exist.")

        customer_id, city = random.choice(customers)
        cur.execute(
            "INSERT INTO orders (customer_id,status,order_date,shipping_city) VALUES (%s,'Pending',%s,%s)",
            (customer_id, datetime.now(), city),
        )
        order_id = cur.lastrowid
        selected = random.sample(products, k=min(random.randint(1, 3), len(products)))
        total = 0.0
        for product_id, price, stock in selected:
            qty = random.randint(1, min(3, stock))
            total += float(price) * qty
            cur.execute(
                "INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (%s,%s,%s,%s)",
                (order_id, product_id, qty, price),
            )
            cur.execute(
                "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                (qty, product_id),
            )
        cur.execute(
            """INSERT INTO payments (order_id,payment_method,payment_status,amount)
               VALUES (%s,%s,'Pending',%s)""",
            (order_id, random.choice(METHODS), round(total, 2)),
        )
        conn.commit()
        print(f"Created simulated order #{order_id} for ₹{total:,.2f}.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
