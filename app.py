import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

from db import read_sql, execute_sql

st.set_page_config(page_title="LiveCart Analytics", page_icon="🛒", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); padding: 14px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("🛒 LiveCart")
st.caption("Real-Time E-Commerce Sales & Order Analytics")
with st.sidebar:
    st.header("Dashboard controls")
    st.write("Refresh the dashboard to load the latest MySQL data.")
    if st.button("🔄 Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.subheader("Add a test order")
    st.caption("This creates a real row in your local database.")
    try:
        customers = read_sql("SELECT customer_id, full_name FROM customers ORDER BY full_name")
        products = read_sql(
            "SELECT product_id, product_name, unit_price, stock_quantity FROM products WHERE active=TRUE ORDER BY product_name"
        )
        if customers and products:
            customer_labels = {f"{c['full_name']} (#{c['customer_id']})": c["customer_id"] for c in customers}
            product_labels = {
                f"{p['product_name']} — ₹{float(p['unit_price']):,.2f} (stock {p['stock_quantity']})": p
                for p in products if p["stock_quantity"] > 0
            }
            with st.form("new_order_form"):
                customer_label = st.selectbox("Customer", list(customer_labels))
                product_label = st.selectbox("Product", list(product_labels))
                quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1)
                submit = st.form_submit_button("Create order", use_container_width=True)
            if submit:
                product = product_labels[product_label]
                if quantity > product["stock_quantity"]:
                    st.error("Not enough stock for that quantity.")
                else:
                    connection = None
                    cursor = None
                    try:
                        from db import get_connection
                        connection = get_connection()
                        cursor = connection.cursor()
                        cursor.execute(
                            """INSERT INTO orders (customer_id,status,order_date,shipping_city)
                               SELECT customer_id,'Pending',NOW(),city FROM customers WHERE customer_id=%s""",
                            (customer_labels[customer_label],),
                        )
                        order_id = cursor.lastrowid
                        cursor.execute(
                            "INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (%s,%s,%s,%s)",
                            (order_id, product["product_id"], int(quantity), product["unit_price"]),
                        )
                        total = float(product["unit_price"]) * int(quantity)
                        cursor.execute(
                            """INSERT INTO payments (order_id,payment_method,payment_status,amount)
                               VALUES (%s,'UPI','Pending',%s)""",
                            (order_id, total),
                        )
                        cursor.execute(
                            "UPDATE products SET stock_quantity=stock_quantity-%s WHERE product_id=%s",
                            (int(quantity), product["product_id"]),
                        )
                        connection.commit()
                        st.success(f"Created order #{order_id} for ₹{total:,.2f}.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as exc:
                        if connection:
                            connection.rollback()
                        st.error(f"Could not create order: {exc}")
                    finally:
                        if cursor:
                            cursor.close()
                        if connection:
                            connection.close()
        else:
            st.info("Run seed_data.py to add customers and products.")
    except Exception as exc:
        st.warning("Database is not ready yet. Follow the setup instructions below.")
        st.caption(str(exc))

@st.cache_data(ttl=10)
def load_kpis():
    rows = read_sql("""
        SELECT
          COALESCE(SUM(CASE WHEN status NOT IN ('Cancelled','Refunded') THEN 1 ELSE 0 END),0) AS active_orders,
          COALESCE(SUM(CASE WHEN status NOT IN ('Cancelled','Refunded') THEN order_total ELSE 0 END),0) AS revenue,
          COALESCE(AVG(CASE WHEN status NOT IN ('Cancelled','Refunded') THEN order_total END),0) AS avg_order_value,
          COALESCE(SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END),0) AS pending_orders
        FROM vw_order_summary
    """)
    return rows[0] if rows else {}

try:
    kpi = load_kpis()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Net sales* ", f"₹{float(kpi['revenue']):,.2f}")
    m2.metric("Eligible orders", f"{int(kpi['active_orders']):,}")
    m3.metric("Average order value", f"₹{float(kpi['avg_order_value']):,.2f}")
    m4.metric("Pending orders", f"{int(kpi['pending_orders']):,}")
    st.caption("*Sales exclude cancelled and refunded orders. Sample data is for demonstration.")

    left, right = st.columns([1.6, 1])
    with left:
        st.subheader("Daily revenue — last 30 days")
        daily = pd.DataFrame(read_sql("""
            SELECT DATE(order_date) AS order_day, SUM(order_total) AS revenue
            FROM vw_order_summary
            WHERE order_date >= CURRENT_DATE - INTERVAL 29 DAY
              AND status NOT IN ('Cancelled','Refunded')
            GROUP BY DATE(order_date)
            ORDER BY order_day
        """))
        if not daily.empty:
            daily["order_day"] = pd.to_datetime(daily["order_day"])
            fig = px.line(daily, x="order_day", y="revenue", markers=True,
                          labels={"order_day": "Date", "revenue": "Revenue (₹)"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet.")

    with right:
        st.subheader("Orders by status")
        status_df = pd.DataFrame(read_sql("""
            SELECT status, COUNT(*) AS order_count
            FROM orders GROUP BY status ORDER BY order_count DESC
        """))
        if not status_df.empty:
            fig = px.pie(status_df, names="status", values="order_count", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No orders yet.")

    left, right = st.columns(2)
    with left:
        st.subheader("Top 5 products by sales")
        top_products = pd.DataFrame(read_sql("""
            SELECT p.product_name,
                   SUM(oi.quantity * oi.unit_price) AS revenue,
                   SUM(oi.quantity) AS units_sold
            FROM order_items oi
            JOIN products p ON p.product_id=oi.product_id
            JOIN orders o ON o.order_id=oi.order_id
            WHERE o.status NOT IN ('Cancelled','Refunded')
            GROUP BY p.product_id,p.product_name
            ORDER BY revenue DESC LIMIT 5
        """))
        if not top_products.empty:
            st.dataframe(top_products, use_container_width=True, hide_index=True)
        else:
            st.info("No product sales yet.")
    with right:
        st.subheader("Low-stock alerts")
        low_stock = pd.DataFrame(read_sql("""
            SELECT product_name, category, stock_quantity
            FROM products WHERE active=TRUE AND stock_quantity <= 20
            ORDER BY stock_quantity, product_name
        """))
        if not low_stock.empty:
            st.dataframe(low_stock, use_container_width=True, hide_index=True)
        else:
            st.success("No products at or below the stock threshold.")

    st.subheader("Latest orders")
    latest = pd.DataFrame(read_sql("""
        SELECT order_id, order_date, customer_name, shipping_city, status, order_total
        FROM vw_order_summary ORDER BY order_date DESC LIMIT 25
    """))
    if not latest.empty:
        latest["order_total"] = latest["order_total"].astype(float).map(lambda v: f"₹{v:,.2f}")
        st.dataframe(latest, use_container_width=True, hide_index=True)
    else:
        st.info("No orders yet.")

    st.subheader("Customer lifetime value")
    customer_df = pd.DataFrame(read_sql("""
        WITH customer_spend AS (
          SELECT c.customer_id, c.full_name,
                 SUM(oi.quantity * oi.unit_price) AS lifetime_spend,
                 COUNT(DISTINCT o.order_id) AS order_count
          FROM customers c
          JOIN orders o ON o.customer_id=c.customer_id
          JOIN order_items oi ON oi.order_id=o.order_id
          WHERE o.status NOT IN ('Cancelled','Refunded')
          GROUP BY c.customer_id,c.full_name
        )
        SELECT full_name, lifetime_spend, order_count,
               DENSE_RANK() OVER (ORDER BY lifetime_spend DESC) AS spend_rank
        FROM customer_spend ORDER BY spend_rank LIMIT 10
    """))
    if not customer_df.empty:
        customer_df["lifetime_spend"] = customer_df["lifetime_spend"].astype(float)
        st.dataframe(customer_df, use_container_width=True, hide_index=True)
    else:
        st.info("Customer spend will appear after orders are added.")

except mysql.connector.Error as exc:
    st.error("Could not connect to MySQL. Check that MySQL is running and your .env settings are correct.")
    st.code(str(exc))
    st.markdown("""
    **Setup checklist**
    1. Start the MySQL server.
    2. Update `.env` with your MySQL username and password.
    3. Run `sql/schema.sql` and `sql/seed.sql` in MySQL Workbench.
    4. Run `python seed_data.py`.
    5. Restart this app.
    """)
except Exception as exc:
    st.error(f"Dashboard error: {exc}")
