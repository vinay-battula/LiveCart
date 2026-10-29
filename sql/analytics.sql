USE livecart;

-- 1. Revenue and order KPIs (cancelled/refunded orders excluded from gross sales)
SELECT
    COUNT(DISTINCT CASE WHEN status <> 'Cancelled' THEN order_id END) AS non_cancelled_orders,
    COALESCE(SUM(CASE WHEN status NOT IN ('Cancelled','Refunded')
                      THEN order_total ELSE 0 END), 0) AS gross_sales,
    COALESCE(AVG(CASE WHEN status NOT IN ('Cancelled','Refunded')
                      THEN order_total END), 0) AS average_order_value
FROM vw_order_summary;

-- 2. Daily revenue for the last 30 days
SELECT DATE(order_date) AS order_day,
       SUM(order_total) AS revenue,
       COUNT(*) AS orders_count
FROM vw_order_summary
WHERE order_date >= CURRENT_DATE - INTERVAL 29 DAY
  AND status NOT IN ('Cancelled','Refunded')
GROUP BY DATE(order_date)
ORDER BY order_day;

-- 3. Top 5 products by revenue
SELECT p.product_name, SUM(oi.quantity * oi.unit_price) AS revenue,
       SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status NOT IN ('Cancelled','Refunded')
GROUP BY p.product_id, p.product_name
ORDER BY revenue DESC
LIMIT 5;

-- 4. Customer lifetime spend with a window function
WITH customer_spend AS (
    SELECT c.customer_id, c.full_name,
           SUM(oi.quantity * oi.unit_price) AS lifetime_spend,
           COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('Cancelled','Refunded')
    GROUP BY c.customer_id, c.full_name
)
SELECT full_name, lifetime_spend, order_count,
       DENSE_RANK() OVER (ORDER BY lifetime_spend DESC) AS spend_rank
FROM customer_spend
ORDER BY spend_rank, full_name;

-- 5. Low-stock alerts
SELECT product_id, product_name, stock_quantity
FROM products
WHERE active = TRUE AND stock_quantity <= 20
ORDER BY stock_quantity;
