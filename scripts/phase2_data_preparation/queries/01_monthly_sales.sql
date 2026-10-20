-- Total monthly sales: the series the forecasting models are trained on.
-- Business question: how much do we sell each month, across all categories?
-- Grain: one row per order_year x order_month.
SELECT order_year, order_month,
printf('%04d-%02d-01', order_year, order_month) AS month_start,
SUM(sales) AS total_sales, SUM(quantity) AS total_quantity,
COUNT (DISTINCT order_id) AS order_count
FROM order_items
GROUP BY order_year, order_month
ORDER BY order_year, order_month;
-- Note: month_start is the first day of the month as ISO text, so pandas can
-- parse it straight into a monthly DatetimeIndex.
-- A month with no orders would produce no row here (not a zero), so the
-- 48-months-no-gaps check lives in tests/test_db_utils_real_db.py.
