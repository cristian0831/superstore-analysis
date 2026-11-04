-- Monthly sales by product category: one series per category.
-- Business question: how much does each category sell each month?
-- Grain: order_year x order_month x category.
SELECT oi.order_year, oi.order_month,
printf('%04d-%02d-01', oi.order_year, oi.order_month) AS month_start,
p.category, SUM(oi.sales) AS total_sales, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.order_year, oi.order_month, p.category
ORDER BY oi.order_year, oi.order_month, p.category;
