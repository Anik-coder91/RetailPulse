

-- RetailPulse: Sales and Inventory Analysis
-- Purpose: Business reporting and inventory monitoring

USE retailpulse;

-- 1. Product performance ranked by revenue
SELECT
    p.product_name,
    SUM(si.quantity) AS units_sold,
    SUM(si.quantity * si.unit_price) AS total_revenue
FROM products AS p
JOIN sale_items AS si
    ON p.product_id = si.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC;

-- 2. Daily sales trends
SELECT
    s.sale_date,
    SUM(si.quantity * si.unit_price) AS daily_revenue,
    SUM(si.quantity) AS units_sold,
    COUNT(DISTINCT s.sale_id) AS total_orders
FROM sales AS s
JOIN sale_items AS si
    ON s.sale_id = si.sale_id
GROUP BY s.sale_date
ORDER BY s.sale_date;

-- 3. Payment method analysis
SELECT
    s.payment_method,
    COUNT(DISTINCT s.sale_id) AS total_orders,
    SUM(si.quantity * si.unit_price) AS total_revenue,
    SUM(si.quantity) AS units_sold
FROM sales AS s
JOIN sale_items AS si
    ON s.sale_id = si.sale_id
GROUP BY s.payment_method
ORDER BY total_revenue DESC;

-- 4. Inventory reorder analysis
SELECT
    product_id,
    product_name,
    category,
    stock_quantity,
    reorder_level,
    stock_quantity - reorder_level AS stock_difference,
    CASE
        WHEN stock_quantity = 0 THEN 'Out of Stock'
        WHEN stock_quantity <= reorder_level THEN 'Reorder Required'
        ELSE 'Sufficient Stock'
    END AS stock_status
FROM products
ORDER BY stock_difference ASC;

-- 5. Overall sales summary
SELECT
    SUM(si.quantity * si.unit_price) AS total_revenue,
    SUM(si.quantity) AS total_units_sold,
    COUNT(DISTINCT s.sale_id) AS total_orders,
    ROUND(
        SUM(si.quantity * si.unit_price)
        / NULLIF(COUNT(DISTINCT s.sale_id), 0),
        2
    ) AS average_order_value
FROM sales AS s
JOIN sale_items AS si
    ON s.sale_id = si.sale_id;
